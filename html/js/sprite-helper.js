"use strict"

var Sprite = {
	getImage: function(kind, id, size)
	{
		var img = document.createElement('img');
		var obj = _sprites[kind][id];
		var height = 48;
		var sprite = obj.image.sprite;

		if ('small' == size) {
			height = 36;
			sprite = 'small_' + sprite;
		}
		else if ('tiny' == size) {
			height = 24;
			sprite = 'tiny_' + sprite;
		}

		var ratio = height / obj.image.h;

		img.src = "img/pix.gif";
		img.alt = obj.name;
		img.title = obj.name;
		img.style.width = Math.round(obj.image.width * ratio) + 'px';
		img.style.height = height + 'px';
		img.style.backgroundImage = "url(img/sprites/" + sprite + ")";
		img.style.backgroundPosition = "-" +
			Math.round(obj.image.x * ratio) + "px -" +
			Math.round(obj.image.y * ratio) + "px";

		return img;
	}
};

var Scoreboard = function(id)
{
	this.board = $(id);
}
Scoreboard.prototype.drawLine = function(team, summoner_name, tier, kda, ratio, gold, cs, items, summoners, champion)
{
	var line = $('.team' + team + ' .template', this.board).clone();
	line.removeClass('template');

	$('.summoner-name .name', line).text(summoner_name);
	$('.summoner-name .tier', line).text(tier);
	$('.kda .details', line).text(kda);
	$('.kda .ratio', line).text(ratio);
	$('.gold .amount', line).text(gold);
	$('.gold .cs', line).text(cs + ' CS');

	var itemsContainer = $('.items', line);
	for (var i = 0; i < items.length; ++i) {
		var item = Sprite.getImage('item', items[i], 'small');
		itemsContainer.append(item);
	}

	$('.summoners .spell0', line).append(Sprite.getImage('summoner', summoners[0], 'tiny'));
	$('.summoners .spell1', line).append(Sprite.getImage('summoner', summoners[1], 'tiny'));
	$('.champion', line).append(Sprite.getImage('champion', champion));

	line.css('display', '');
	$('.team' + team + ' tbody').append(line);
}