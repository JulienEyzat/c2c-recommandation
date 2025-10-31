# External libs
import argparse
# Internal libs
import outings_distancer
import outings_loader
import outings_preprocess

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(
        prog='outings_recommandation.py',
        description='This program find similar outings from camptocamp'
    )
    parser.add_argument("-d", '--input-directory', help='directory containing the data from the downloader.py program')
    parser.add_argument("-o", "--outing-id", type=int, help="outing id of the camptocamp outing to compare")
    args = parser.parse_args()
    # Processing
    print("Loading source outings")
    oloader = outings_loader.OutingsLoader(args.input_directory)
    df = oloader.load()
    print("Preprocess outings")
    opreprocess = outings_preprocess.OutingsPreprocess()
    df = opreprocess.preprocess(df)
    print("Calculate distance from specific outing")
    odistancer = outings_distancer.OutingsDistancer(df)
    output = odistancer.get_sim_outings_from_outing(args.outing_id)
    print(output)