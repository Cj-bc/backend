#!/usr/bin/env bash
#
# this script outputs PDF file of QR cards list.
#
# copyright (c) 2018 Sakutendev

trap 'rm src/qr/*.png src/*.html' 2
echo "Done.\nAll processes are done properly.exit."
if ! [ -e src/cards.html ]; then
  echo "Generating html..."
  pipenv run python mkhtml.py
  echo "done."
else
  echo "html file detected. Skip generating HTML"
fi
echo "Generating PDF..."
wkhtmltopdf --encoding 'utf-8' --lowquality cards.html cards.pdf
