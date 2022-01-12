import argparse
from components import models, painters, writers, colored_output
from components.runners import dir_run, file_run, file_run_monitor, webcam_run_monitor
import os

modello = [
    ".\\mpi\\pose_iter_160000.caffemodel",
    ".\\mpi\\pose_deploy_linevec_faster_4_stages.prototxt",
]


def main():
    parser = argparse.ArgumentParser(description="Process images")
    parser.add_argument("--videoIn", "-i", type=str, help="input file")
    parser.add_argument(
        "--videoOut",
        "-o",
        type=str,
        help="file di output opzionale, nel caso si abbia dato una directory con -d sarà la directory di output",
    )
    parser.add_argument("--dir", "-d", type=str, help="directory source")
    parser.add_argument(
        "-m", default=False, action="store_true", help="persone multiple"
    )
    parser.add_argument(
        "-g", default=False, action="store_true", help="usa accelerazione gpu"
    )
    parser.add_argument(
        "-p", default=False, action="store_true", help="oscuramento volti"
    )

    args = parser.parse_args()

    # get Requested Model
    model = models.model_factory(args.m, args.g, modello[0], modello[1])
    model.init_net()

    # get Requested Painter
    painter = painters.painter_factory(args.p)

    outputter = colored_output.ColoredOutput()
    # get requested writer depending on the arguments
    if args.dir:
        dir_run(model, painter, args.dir, args.videoOut, outputter)
    elif args.videoIn and args.videoOut:
        file_run(model, painter, args.videoIn, args.videoOut, outputter)
    elif args.videoIn:
        file_run_monitor(model, painter, args.videoIn, outputter)
    elif not args.videoIn and args.videoOut:
        parser.print_help()
        exit(-1)
    else:
        webcam_run_monitor(model, painter)


if __name__ == "__main__":
    main()
