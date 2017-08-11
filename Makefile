all:
	python fontlie.py
view:
	xdg-open docs/index.html

clean:
	rm -vrf docs/fonts/* index_*
