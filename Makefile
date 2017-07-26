all:
	python fontlie.py
view:
	xdg-open demo.html

clean:
	rm -vf fonts/helvetica-bold_*  demo.html demo_fontface.css
