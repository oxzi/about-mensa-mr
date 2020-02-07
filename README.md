# about:mensa - Canteen analysis of the University of Marburg

A small analysis project of the canteens of the University of Marburg. This
started as an evening project together with
[@hoechst](https://github.com/jonashoechst/mensalysis) and was extended for a
[hackslam](https://hsmr.cc/Hackslam/2020-02-07).

The data was extracted from [OpenMensa](https://openmensa.org/), which supplies
a huge archive of canteens and their food. Thanks a lot!

The extraction script is `openmensa.py` and the analysis is present in
`mensa_prices.ipynb` as a Jupyter notebook.

```sh
jupyter-notebook

# export notebook as slides
jupyter nbconvert mensa_prices.ipynb --to slides --post serve
```
