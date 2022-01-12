import argparse
from components import Exceptions, models, painters, writers
from components.runners import run_simulation_to_file, run_simulation_to_monitor
from components.file_check import check_file_type
import os

modello = [
    ".\\mpi\\pose_iter_160000.caffemodel",
    ".\\mpi\\pose_deploy_linevec_faster_4_stages.prototxt",
]


def dir_run(
    model: models.Model,
    painter: painters.Painter,
    dir_in: str,
    dir_out: str,
) -> None:
    if not os.path.isdir(dir_out):
        os.mkdir(dir_out)
    writer = None
    img_writer = writers.ImageWriter("")
    video_writer = writers.VideoWriter("")
    # loop over all files in directory
    for filename in os.listdir(dir_in):
        f = os.path.join(dir_in, filename)
        fout = os.path.join(dir_out, f"OUT{filename}")
        # checking if f is a file
        if os.path.isfile(f):
            try:
                file_type = check_file_type(f)
                print(f"Currently working on {f}")
                writer = img_writer if file_type == "image" else video_writer
                writer.change_file(f, fout)
                writer.init_writer()
                run_simulation_to_file(model, writer, painter)
                writer.close()
            except Exceptions.FileTypeException:
                print(f"{f} doesen't have the correct video or image format")


def file_run(
    model: models.Model,
    painter: painters.Painter,
    file_input: str,
    file_output: str,
) -> None:
    input_type = ""
    output_type = ""
    try:
        input_type = check_file_type(file_input)
    except Exceptions.FileTypeException:
        print("errore estensione file input")
        exit()
    try:
        output_type = check_file_type(file_output)
    except Exceptions.FileTypeException:
        _, ext = os.path.splitext(file_input)
        file_output, _ = os.path.splitext(file_output)
        file_output = file_output + ext
        output_type = input_type
    if input_type != output_type:
        print("Estensione errata dell'output")
        exit(-1)

    writer = (
        writers.ImageWriter(file_input, file_output)
        if input_type == "image"
        else writers.VideoWriter(file_input, file_output)
    )

    writer.init_writer()
    run_simulation_to_file(model, writer, painter)
    writer.close()


def file_run_monitor(
    model: models.Model, painter: painters.Painter, file_input: str
) -> None:
    input_type = ""
    try:
        input_type = check_file_type(file_input)
    except Exceptions.FileTypeException:
        print("errore estensione file input")
        exit()
    writer = writers.FileMonitorWriter(file_input)
    writer.init_writer()
    waiter = writer.wait_key_image if input_type == "image" else writer.wait_key_video
    run_simulation_to_monitor(model, writer, painter, waiter)
    writer.close()


def webcam_run_monitor(model: models.Model, painter: painters.Painter) -> None:
    writer = writers.WebCamMonitorWriter()
    writer.init_writer()
    run_simulation_to_monitor(model, writer, painter, writer.wait_key_video)
    writer.close()


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

    # get requested writer depending on the arguments
    if args.dir and os.path.isdir(args.dir):
        if not args.videoOut:
            print("Argument -o, --videoOut is MISSING")
            exit(-1)
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
    main()
