import argparse
import components
from colorama import init

modello = [
    ".\\mpi\\pose_iter_160000.caffemodel",
    ".\\mpi\\pose_deploy_linevec_faster_4_stages.prototxt",
]


def main():
    parser = argparse.ArgumentParser(description="Process images")
    parser.add_argument(
        "--videoIn",
        "-i",
        type=str,
        help="relative or absolute path to an image to ingest, if omitted default to the camera",
    )
    parser.add_argument(
        "--videoOut",
        "-o",
        type=str,
        help="path to the output image, if omitted an image will pop up.\nIn case you have given a directory with -d it will be the (requested) output directory",
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        help="select a directory to process (overrides -i), -o behaviour changes to the output directory's name (requested)",
    )
    parser.add_argument(
        "-m",
        default=False,
        action="store_true",
        help="multiple people detection, default to single detection",
    )
    parser.add_argument(
        "-g",
        default=False,
        action="store_true",
        help="use GPU acceleration, default CPU only",
    )
    parser.add_argument(
        "-p",
        default=False,
        action="store_true",
        help="private mode: cover all detected faces",
    )

    args = parser.parse_args()

    # get Requested Model
    model = models.model_factory(args.m, args.g, modello[0], modello[1])
    model.init_net()

    # get Requested Painter
    painter = painters.painter_factory(args.p)

    # run detections depending on the arguments
    if args.dir:
        dir_run(model, painter, args.dir, args.videoOut)
    elif args.videoIn and args.videoOut:
        file_run(model, painter, args.videoIn, args.videoOut)
    elif args.videoIn:
        file_run_monitor(model, painter, args.videoIn)
    elif not args.videoIn and args.videoOut:
        parser.print_help()
        exit(-1)
    else:
        webcam_run_monitor(model, painter)


if __name__ == "__main__":
    init()
    main()
