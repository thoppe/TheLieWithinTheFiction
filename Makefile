all:
	python fontlie.py
view:
	xdg-open index.html

clean:
	rm -vf fonts/*_m?.otf  index.html *_fontface.css	
