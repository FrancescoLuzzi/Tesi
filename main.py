import argparse
from ModelWrapper import Wrapper
import os

modello = [
    ".\\mpi\\pose_iter_160000.caffemodel",
    ".\\mpi\\pose_deploy_linevec_faster_4_stages.prototxt",
]


def main():
    parser = argparse.ArgumentParser(description="Process images")
    parser.add_argument("--videoIn", "-i", type=str, default="0", help="input file")
    parser.add_argument(
        "--videoOut",
        "-o",
        type=str,
        help="file di output opzionale, nel caso si abbia dato una directory con -d sarà la directory di arrivo",
    )
    parser.add_argument("--dir", "-d", type=str, help="directory source")
    parser.add_argument(
        "-m", default=False, action="store_true", help="persone multiple"
    )
    parser.add_argument("-g", default=False, action="store_true", help="usa gpu")
    parser.add_argument(
        "-p", default=False, action="store_true", help="oscuramento volti"
    )

    args = parser.parse_args()

    if args.dir != None and os.path.isdir(args.dir) and args.videoOut != None:
        if not os.path.isdir(args.videoOut):
            os.mkdir(args.videoOut)
        wrapper = Wrapper("", modello[0], modello[1], args.videoOut, args.m, args.p)
        wrapper.init_net(args.g)
        for filename in os.listdir(args.dir):
            f = os.path.join(args.dir, filename)
            print("Currently doing {}".format(f))
            fout = os.path.join(args.videoOut, "OUT{}".format(filename))
            # checking if it is a file
            if os.path.isfile(f):
                wrapper.file_path = f
                wrapper.output_path = fout
                wrapper.run_simulation()
    else:
        out = args.videoOut
        if out != None:
            out = out + ".jpg"
        wrapper = Wrapper(args.videoIn, modello[0], modello[1], out, args.m, args.p)
        wrapper.init_net(args.g)
        wrapper.run_simulation()


if __name__ == "__main__":
    main()
