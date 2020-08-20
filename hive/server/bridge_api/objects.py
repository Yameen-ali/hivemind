"""Handles building condenser-compatible response objects."""

import logging
import ujson as json

from hive.server.common.mutes import Mutes
from hive.server.common.helpers import json_date
from hive.server.database_api.methods import find_votes, VotesPresentation
from hive.utils.normalize import sbd_amount
from hive.indexer.votes import Votes


log = logging.getLogger(__name__)

# pylint: disable=too-many-lines

async def load_profiles(db, names):
    """`get_accounts`-style lookup for `get_state` compat layer."""
    sql = """SELECT id, name, display_name, about, reputation, vote_weight,
                    created_at, post_count, profile_image, location, website,
                    cover_image, rank, following, followers, active_at
               FROM hive_accounts WHERE name IN :names"""
    rows = await db.query_all(sql, names=tuple(names))
    return [_condenser_profile_object(row) for row in rows]

async def load_posts_reblogs(db, ids_with_reblogs, truncate_body=0):
    """Given a list of (id, reblogged_by) tuples, return posts w/ reblog key."""
    post_ids = [r[0] for r in ids_with_reblogs]
    reblog_by = dict(ids_with_reblogs)
    posts = await load_posts(db, post_ids, truncate_body=truncate_body)

    # Merge reblogged_by data into result set
    for post in posts:
        rby = set(reblog_by[post['post_id']].split(','))
        rby.discard(post['author'])
        if rby:
            post['reblogged_by'] = list(rby)

    return posts

ROLES = {-2: 'muted', 0: 'guest', 2: 'member', 4: 'mod', 6: 'admin', 8: 'owner'}

async def load_posts_keyed(db, ids, truncate_body=0):
    """Given an array of post ids, returns full posts objects keyed by id."""
    # pylint: disable=too-many-locals
    assert ids, 'no ids passed to load_posts_keyed'

    # fetch posts and associated author reps
    sql = """
        SELECT
            hp.id,
            hp.community_id,
            hp.author,
            hp.permlink,
            hp.title,
            hp.body,
            hp.category,
            hp.depth,
            hp.promoted,
            hp.payout,
            hp.pending_payout,
            hp.payout_at,
            hp.is_paidout,
            hp.children,
            hp.votes,
            hp.created_at,
            hp.updated_at,
            hp.rshares,
            hp.json,
            hp.is_hidden,
            hp.is_grayed,
            hp.total_votes,
            hp.flag_weight,
            hp.parent_author,
            hp.parent_permlink,
            hp.curator_payout_value,
            hp.root_author,
            hp.root_permlink,
            hp.max_accepted_payout,
            hp.percent_hbd,
            hp.allow_replies,
            hp.allow_votes,
            hp.allow_curation_rewards,
            hp.beneficiaries,
            hp.url,
            hp.root_title
        FROM hive_posts_view hp
        WHERE hp.id IN :ids
    """
    result = await db.query_all(sql, ids=tuple(ids))
    author_map = await _query_author_map(db, result)

    # TODO: author affiliation?
    ctx = {}
    posts_by_id = {}
    author_ids = {}
    post_cids = {}
    for row in result:
        row = dict(row)
        author = author_map[row['author']]
        author_ids[author['id']] = author['name']

        row['author_rep'] = author['reputation']
        post = _bridge_post_object(row, truncate_body=truncate_body)
        post['active_votes'] = await find_votes({'db':db}, {'author':row['author'], 'permlink':row['permlink']})

        post['blacklists'] = Mutes.lists(post['author'], author['reputation'])

        posts_by_id[row['post_id']] = post
        post_cids[row['post_id']] = row['community_id']

        cid = row['community_id']
        if cid:
            if cid not in ctx:
                ctx[cid] = []
            ctx[cid].append(author['id'])

    # TODO: optimize
    titles = {}
    roles = {}
    for cid, account_ids in ctx.items():
        sql = "SELECT title FROM hive_communities WHERE id = :id"
        titles[cid] = await db.query_one(sql, id=cid)
        sql = """SELECT account_id, role_id, title
                   FROM hive_roles
                  WHERE community_id = :cid
                    AND account_id IN :ids"""
        roles[cid] = {}
        ret = await db.query_all(sql, cid=cid, ids=tuple(account_ids))
        for row in ret:
            name = author_ids[row['account_id']]
            roles[cid][name] = (row['role_id'], row['title'])

    for pid, post in posts_by_id.items():
        author = post['author']
        cid = post_cids[pid]
        if cid:
            post['community'] = post['category'] # TODO: True?
            post['community_title'] = titles[cid] or post['category']
            role = roles[cid][author] if author in roles[cid] else (0, '')
            post['author_role'] = ROLES[role[0]]
            post['author_title'] = role[1]
        else:
            post['stats']['gray'] = ('irredeemables' in post['blacklists']
                                     or len(post['blacklists']) >= 2)
        post['stats']['hide'] = 'irredeemables' in post['blacklists']


    sql = """SELECT id FROM hive_posts
              WHERE id IN :ids AND is_pinned = '1' AND counter_deleted = 0"""
    for pid in await db.query_col(sql, ids=tuple(ids)):
        if pid in posts_by_id:
            posts_by_id[pid]['stats']['is_pinned'] = True

    return posts_by_id

async def load_posts(db, ids, truncate_body=0):
    """Given an array of post ids, returns full objects in the same order."""
    if not ids:
        return []

    # posts are keyed by id so we can return output sorted by input order
    posts_by_id = await load_posts_keyed(db, ids, truncate_body=truncate_body)

    # in rare cases of cache inconsistency, recover and warn
    missed = set(ids) - posts_by_id.keys()
    if missed:
        log.info("get_posts do not exist in cache: %s", repr(missed))
        for _id in missed:
            ids.remove(_id)
            sql = """
                SELECT
                    hp.id, ha_a.name as author, hpd_p.permlink as permlink, depth, created_at, counter_deleted
                FROM
                    hive_posts hp
                INNER JOIN hive_accounts ha_a ON ha_a.id = hp.author_id
                INNER JOIN hive_permlink_data hpd_p ON hpd_p.id = hp.permlink_id
                WHERE id = :id and counter_deleted = 0 """
            post = await db.query_row(sql, id=_id)
            if post is None:
                # TODO: This should never happen. See #173 for analysis
                log.error("missing post: id %i", _id)
            else:
                log.info("requested deleted post: %s", dict(post))

    return [posts_by_id[_id] for _id in ids]

async def _query_author_map(db, posts):
    """Given a list of posts, returns an author->reputation map."""
    if not posts: return {}
    names = tuple({post['author'] for post in posts})
    sql = "SELECT id, name, reputation FROM hive_accounts WHERE name IN :names"
    return {r['name']: r for r in await db.query_all(sql, names=names)}

def _condenser_profile_object(row):
    """Convert an internal account record into legacy-steemd style."""

    blacklists = Mutes.lists(row['name'], row['reputation'])

    return {
        'id': row['id'],
        'name': row['name'],
        'created': json_date(row['created_at']),
        'active': json_date(row['active_at']),
        'post_count': row['post_count'],
        'reputation': row['reputation'],
        'blacklists': blacklists,
        'stats': {
            'sp': int(row['vote_weight'] * 0.0005037),
            'rank': row['rank'],
            'following': row['following'],
            'followers': row['followers'],
        },
        'metadata': {
            'profile': {'name': row['display_name'],
                        'about': row['about'],
                        'website': row['website'],
                        'location': row['location'],
                        'cover_image': row['cover_image'],
                        'profile_image': row['profile_image'],
                       }}}

def _bridge_post_object(row, truncate_body=0):
    """Given a hive_posts row, create a legacy-style post object."""
    paid = row['is_paidout']

    post = {}
    post['post_id'] = row['id']
    post['author'] = row['author']
    post['permlink'] = row['permlink']
    post['category'] = row.get('category', 'undefined')

    post['title'] = row['title']
    post['body'] = row['body'][0:truncate_body] if truncate_body else row['body']
    post['json_metadata'] = json.loads(row['json'])

    post['created'] = json_date(row['created_at'])
    post['updated'] = json_date(row['updated_at'])
    post['depth'] = row['depth']
    post['children'] = row['children']
    post['net_rshares'] = row['rshares']

    post['is_paidout'] = row['is_paidout']
    post['payout_at'] = json_date(row['payout_at'])
    post['payout'] = float(row['payout'] + row['pending_payout'])
    post['pending_payout_value'] = _amount(0 if paid else post['payout'])
    post['author_payout_value'] = _amount(0) # supplemented below
    post['curator_payout_value'] = _amount(0) # supplemented below
    post['promoted'] = _amount(row['promoted'])

    post['replies'] = []
    post['author_reputation'] = float(row['author_rep'])

    post['stats'] = {
        'hide': row['is_hidden'],
        'gray': row['is_grayed'],
        'total_votes': row['total_votes'],
        'flag_weight': float(row['flag_weight'])} # TODO: down_weight


    #post['author_reputation'] = rep_to_raw(row['author_rep'])

    post['url'] = row['url']
    post['beneficiaries'] = row['beneficiaries']
    post['max_accepted_payout'] = row['max_accepted_payout']
    post['percent_hbd'] = row['percent_hbd']

    if paid:
        curator_payout = sbd_amount(row['curator_payout_value'])
        post['author_payout_value'] = _amount(row['payout'] - curator_payout)
        post['curator_payout_value'] = _amount(curator_payout)

    # TODO: re-evaluate
    if row['depth'] > 0:
        post['parent_author'] = row['parent_author']
        post['parent_permlink'] = row['parent_permlink']
        post['title'] = 'RE: ' + row['root_title'] # PostSummary & comment context

    return post

def _amount(amount, asset='HBD'):
    """Return a steem-style amount string given a (numeric, asset-str)."""
    assert asset == 'HBD', 'unhandled asset %s' % asset
    return "%.3f HBD" % amount
