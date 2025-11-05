# External libs
import argparse
# Internal libs
import routes_distancer
import routes_loader
import routes_preprocess

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(
        prog='routes_recommandation.py',
        description='This program find similar routes from camptocamp'
    )
    parser.add_argument("-d", '--input-directory', help='directory containing the data from the downloader.py program')
    parser.add_argument("-r", "--route-id", type=int, help="route id of the camptocamp route to compare")
    args = parser.parse_args()
    # Processing
    print("Loading source routes")
    oloader = routes_loader.RoutesLoader(args.input_directory)
    df = oloader.load()
    # print(df.loc[df["durations"].str.contains(","), "document_id"])
    print("Preprocess routes")
    rpreprocess = routes_preprocess.RoutesPreprocess()
    df = rpreprocess.preprocess(df)
    print("Calculate distance from specific route")
    rdistancer = routes_distancer.RoutesDistancer(df)
    output = rdistancer.get_sim_routes_from_route(args.route_id)
    print(output)