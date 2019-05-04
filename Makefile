
all:
	python citation-wordcloud.py
	python citation-heatmap.py
	python characters-representation.py
	python narrative-chart.py
	- cp out/* blog-kaamelott-dir

update_data:
	wget https://raw.githubusercontent.com/2ec0b4/kaamelott-soundboard/master/sounds/sounds.json
