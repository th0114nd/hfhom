all: graph_quad plink_classes plink_load seifert weighted_graph ndqf smith

graph_quad:
	python test_graph_quad.py
plink_classes:
	python test_plink_classes.py
plink_load:
	python test_plink_load.py
seifert:
	python test_seifert.py
weighted_graph:
	python test_weighted_graph.py
ndqf:
	python test_ndqf.py
smith:
	python test_smith.py
clean:
	rm *.pyc
