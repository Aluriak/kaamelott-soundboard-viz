
all:
	python -m plot-stats
	xdg-open out.html

update_data:
	wget https://raw.githubusercontent.com/2ec0b4/kaamelott-soundboard/master/sounds/sounds.json
