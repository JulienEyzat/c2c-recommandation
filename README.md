# INSTALLATION

First, you need to install python.

Then, install the librairies from the requierements.txt file. For example with pip :

    pip install -r requirements.txt

# USAGE

Example usage for outings :

    python outings_recommandation.py -d ../data -o 1826832

Example usage for routes :

    python routes_recommandation.py -d ../data -r 863754

Options
- -d: The path to the directory containing the output of c2c_downloader (see https://github.com/JulienEyzat/c2c-downloader).
- -o: The outing id you want to find similar outings to. The id can be found as the number on the camptocamp URL of an outing.
- -r: The route id you want to find similar routes to. The id can be found as the number on the camptocamp URL of a route.

# NEXT STEPS

## Routes

- handle orientations as circular data