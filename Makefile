all:
	python fontlie.py
view:
	xdg-open docs/index.html

clean:
	rm -vf docs/*.otf docs/index* 
