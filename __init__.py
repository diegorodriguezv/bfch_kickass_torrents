import chanutils.torrent
from chanutils import get_doc, get_json, select_all, select_one, get_attr
from chanutils import get_text, get_text_content, replace_entity, byte_size
from playitem import TorrentPlayItem, PlayItemList

_SEARCH_URL = "http://kickass.to/json.php"
_CAT_WHITELIST = ['Movies', 'TV', 'Anime', 'Music']

_FEEDLIST = [
  {'title':'Movies', 'url':'http://kickass.to/movies/'},
  {'title':'TV Shows', 'url':'http://kickass.to/tv/'},
  {'title':'Anime', 'url':'http://kickass.to/anime/'},
  {'title':'Music', 'url':'http://kickass.to/music/'},
  {'title':'Lossless Music', 'url':'http://kickass.to/lossless/'},
]

def name():
  return 'Kickass Torrents'

def image():
  return 'icon.png'

def description():
  return "Kickass Torrents Channel (<a target='_blank' href='http://kickass.to'>http://kickass.to</a>)."

def feedlist():
  return _FEEDLIST

def feed(idx):
  doc = get_doc(_FEEDLIST[idx]['url'], proxy=True)
  rtree = select_all(doc, 'tr.odd, tr.even')
  results = PlayItemList()
  for l in rtree:
    el = select_one(l, 'a.cellMainLink')
    title = get_text(el)
    el = select_one(l, "a[title='Torrent magnet link']")
    # DMCA takedown
    if el is None:    
      continue
    url = get_attr(el, 'href')
    img = '/img/icons/film.svg'
    cat = _FEEDLIST[idx]['title']
    if cat.endswith('Music'):
      img = '/img/icons/music.svg'
    el = select_one(l, "td.nobr")
    size = get_text_content(el)
    el = select_one(l, "td.green")
    seeds = get_text(el)
    el = select_one(l, "td.red")
    peers = get_text(el)
    subtitle = chanutils.torrent.subtitle(size, seeds, peers)
    results.add(TorrentPlayItem(title, img, url, subtitle))
  return results

def search(q):
  data = get_json(_SEARCH_URL, params={'q':q}, proxy=True)
  if not 'list' in data:
    return []
  rtree = data['list']
  results = PlayItemList()
  for r in rtree:
    cat = r['category']
    if not (cat in _CAT_WHITELIST):
      continue
    title = replace_entity(r['title'])
    img = '/img/icons/film.svg'
    if cat == 'Music':
      img = '/img/icons/music.svg'
    size = byte_size(r['size'])
    subtitle = chanutils.torrent.subtitle(size, r['seeds'], r['peers'])
    url = r['torrentLink']
    results.add(TorrentPlayItem(title, img, url, subtitle))
  return results
