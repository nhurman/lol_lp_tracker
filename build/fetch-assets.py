import urllib.request
import zipfile
import tarfile
import os
import json

def write_to(in_buffer, out_file):
	with open(out_file, 'wb+') as f:
		f.write(in_buffer)

def fetch_tier_icons():
	url = 'https://s3-us-west-1.amazonaws.com/riot-api/img/tier-icons.zip'
	zipfile_name = 'tmp/league-icons.zip'
	icons_outpath = '../html/img/tier_icons'

	print('Downloading tiers icons')
	urllib.request.urlretrieve(url, zipfile_name)

	dec_to_roman = {
		1: 'i',
		2: 'ii',
		3: 'iii',
		4: 'iv',
		5: 'v'
	}

	try:
		os.makedirs(icons_outpath)
	except OSError:
		pass

	print('Extracting tier icons')
	with zipfile.ZipFile(zipfile_name) as zf:
		write_to(zf.read('base_icons/challenger.png'), os.path.join(icons_outpath, 'challenger_i.png'))
		write_to(zf.read('base_icons/master.png'), os.path.join(icons_outpath, 'master_i.png'))
		write_to(zf.read('base_icons/provisional.png'), os.path.join(icons_outpath, 'unranked.png'))

		for tier in ('bronze', 'silver', 'gold', 'platinum', 'diamond'):
			for division in range(1, 6):
				file_name = 'tier_icons/' + tier + '_' + dec_to_roman[division] + '.png'
				out_path = os.path.join(icons_outpath, os.path.basename(file_name))
				write_to(zf.read(file_name), out_path)

	os.unlink(zipfile_name)


def fetch_ddragon():
	realm_url = 'https://ddragon.leagueoflegends.com/realms/euw.json'
	archive_name = 'tmp/ddragon.tgz'
	sprites_outpath = '../html/img/sprites/'
	json_outpath =  '../html/js/'

	try:
		os.makedirs(sprites_outpath)
	except OSError:
		pass

	response = urllib.request.urlopen(realm_url)
	data = response.read()
	realm = json.loads(data.decode('utf-8'))

	url = realm['cdn'] + '/dragontail-' + realm['dd'] + '.tgz'
	print('Downloading dragontail version ' + realm['dd'])
	urllib.request.urlretrieve(url, archive_name)

	sprites = {}
	with tarfile.open(archive_name) as tf:
		for object_type in ('champion', 'item', 'summoner'):
			print('Stripping json for ' + object_type + 's')
			data = tf.extractfile('./' + realm['dd'] + '/data/en_GB/' + object_type + '.json').read()
			objects = json.loads(data.decode('utf-8'))
			stripped_objects = {}

			for obj_name in objects['data']:
				obj = objects['data'][obj_name]
				key = obj['key'] if 'key' in obj else obj_name
				stripped_objects[key] = {
					'name': obj['name'],
					'image': {key:obj['image'][key] for key in ('x', 'y', 'w', 'h', 'sprite', 'full')}
				}

			sprites[object_type] = stripped_objects

		with open(os.path.join(json_outpath, 'sprites.js'), 'w+') as f:
			f.write('var _sprites = ')
			f.write(json.dumps(sprites))
			f.write(';\n')

		print('Extracting sprites')
		sprite_names = [n for n in tf.getnames() if n.startswith('./' + realm['dd'] + '/img/sprite/')]
		for name in sprite_names:
			write_to(tf.extractfile(name).read(), os.path.join(sprites_outpath, os.path.basename(name)))

	os.unlink(archive_name)

if __name__ == '__main__':
	try:
		os.mkdir('tmp')
	except OSError:
		pass

	fetch_tier_icons()
	fetch_ddragon()

	os.rmdir('tmp')