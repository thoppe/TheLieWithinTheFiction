all:
	python fontlie.py source.html docs/index.html

M1:
	python fontlie.py Matilda1.html docs/Matilda1/index.html

view:
	xdg-open docs/index.html

clean:
	rm -vf docs/*.otf docs/index* 
