all:
	python fontlie.py
view:
	xdg-open demo.html

clean:
	rm -vf fonts/*_m?.otf  demo.html *_fontface.css	
