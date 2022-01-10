import argparse
from components.Exceptions import FileException

import components.models
from components.runner import run_simulation_to_file, run_simulation_to_monitor
import components.writer
import components.painter
from components.file_check import check_file_type
import os

modello = [
    ".\\mpi\\pose_iter_160000.caffemodel",
    ".\\mpi\\pose_deploy_linevec_faster_4_stages.prototxt",
]


def dir_run(
    model: components.models.Model,
    painter: components.painter.Painter,
    dir_in: str,
    dir_out: str,
) -> None:
    if not os.path.isdir(dir_out):
        os.mkdir(dir_out)
    writer = None
    img_writer = components.writer.ImageWriter("")
    video_writer = components.writer.VideoWriter("")
    # loop over all files in directory
    for filename in os.listdir(dir_in):
        f = os.path.join(dir_in, filename)
        print(f"Currently working on {f}")
        fout = os.path.join(dir_out, f"OUT{filename}")
        # checking if f is a file
        if os.path.isfile(f):
            file_type = check_file_type(f)
            if file_type == "image":
                writer = img_writer
            else:
                writer = video_writer
            writer.change_file(f, fout)
            writer.init_writer()
            run_simulation_to_file(model, writer, painter)
            writer.close()


def file_run(
    model: components.models.Model,
    painter: components.painter.Painter,
    file_input: str,
    file_output: str,
) -> None:
    writer = None
    input_type = ""
    output_type = ""
    try:
        input_type = check_file_type(file_input)
    except FileException:
        print("errore estensione file input")
        exit()
    try:
        output_type = check_file_type(file_output)
    except FileException:
        _, ext = os.path.splitext(file_input)
        file_output, _ = os.path.splitext(file_output)
        file_output = file_output + ext
        output_type = input_type
    if input_type != output_type:
        print("Estensione errata dell'output")
        exit(-1)
    if input_type == "image":
        writer = components.writer.ImageWriter(file_input, file_output)
    else:
        writer = components.writer.VideoWriter(file_input, file_output)
    writer.init_writer()
    run_simulation_to_file(model, writer, painter)
    writer.close()


def file_run_monitor(
    model: components.models.Model, painter: components.painter.Painter, file_input: str
) -> None:
    input_type = ""
    writer = None
    try:
        input_type = check_file_type(file_input)
    except FileException:
        print("errore estensione file input")
        exit()
    writer = components.writer.FileMonitorWriter(file_input)
    writer.init_writer()
    if input_type == "image":
        run_simulation_to_monitor(model, writer, painter, writer.wait_key_image)
    else:
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
    model = components.models.model_factory(args.m, args.g, modello[0], modello[1])
    model.init_net()

    # get Requested Painter
    painter = components.painter.painter_factory(args.p)

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
        writer = components.writer.WebCamMonitorWriter()
        writer.init_writer()
        run_simulation_to_monitor(model, writer, painter, writer.wait_key_video)
        writer.close()


if __name__ == "__main__":
    main()
