
gen-viz:
	python citation-wordcloud.py
	python citation-heatmap.py
	python characters-representation.py
	python narrative-chart.py
	python interaction-graph.py
	- cp out/* blog-kaamelott-dir

update-data:
	cd resources && $(MAKE) update_data


all: update-data gen-viz
