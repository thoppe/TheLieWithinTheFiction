all:
	echo "Choose a style to run"

example:
	python fontlie.py source.html docs/index.html

M1:
	python fontlie.py Matilda1.html docs/Matilda1/index.html --use_nbsp

M2:
	python fontlie.py Matilda2.html docs/Matilda2/index.html --use_nbsp

M3:
	python fontlie.py Matilda3.html docs/Matilda3/index.html --use_nbsp

C1:
	python fontlie.py Chesney1.html docs/Chesney1/index.html --use_nbsp

view:
	xdg-open docs/index.html

clean:
	rm -vf docs/*.otf docs/index* 
