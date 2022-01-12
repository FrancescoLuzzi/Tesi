import argparse
from components import models, painters, writers, colored_output
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
    outputter: colored_output.ColoredOutput,
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
            file_type = check_file_type(f)
            if not file_type:
                outputter.print_error(
                    f"{f} doesen't have the correct video or image format"
                )
                continue
            outputter.print_info(f"Currently working on {f}")
            writer = img_writer if file_type == "image" else video_writer
            writer.change_file(f, fout)
            writer.init_writer()
            run_simulation_to_file(model, writer, painter)
            writer.close()
            outputter.print_ok(f"Detection on {f} successfully completed!")


def file_run(
    model: models.Model,
    painter: painters.Painter,
    file_input: str,
    file_output: str,
    outputter: colored_output.ColoredOutput,
) -> None:
    """Given a model, a painter and a file_input path and a file_output"""
    if not os.path.isfile(file_input):
        outputter.print_error("The file doesen't exists. Check file_input name!")
        exit(-1)
    input_type = check_file_type(file_input)
    if not input_type:
        outputter.print_error(
            "File_input's file extension is not for videos or images!"
        )
        exit(-1)

    output_type = check_file_type(file_output)
    if output_type != input_type:
        outputter.print_info(
            f"Output file type is {output_type=} not consistent with the {input_type=}.\nChanged it to the right extension.\n"
        )
        output_type = ""
    if not output_type:
        _, ext = os.path.splitext(file_input)
        file_output, _ = os.path.splitext(file_output)
        file_output = file_output + ext

    writer = (
        writers.ImageWriter(file_input, file_output)
        if input_type == "image"
        else writers.VideoWriter(file_input, file_output)
    )

    writer.init_writer()
    run_simulation_to_file(model, writer, painter)
    writer.close()
    outputter.print_ok(f"{file_input} as been elaborated, {file_output=}")


def file_run_monitor(
    model: models.Model,
    painter: painters.Painter,
    file_input: str,
    outputter: colored_output.ColoredOutput,
) -> None:
    """Given a model, a painter and a file_input path, depending on this last one extension, get image/video input\n
    and displays the output to a window as an image/video"""
    if not os.path.isfile(file_input):
        outputter.print_error("The file doesen't exists. Check file_input name!")
        exit()
    input_type = check_file_type(file_input)
    if not input_type:
        outputter.print_error(
            "File_input's file extension is not for videos or images!"
        )
        exit()
    writer = writers.FileMonitorWriter(file_input)
    writer.init_writer()
    waiter = writer.wait_key_image if input_type == "image" else writer.wait_key_video
    run_simulation_to_monitor(model, writer, painter, waiter)
    writer.close()


def webcam_run_monitor(model: models.Model, painter: painters.Painter) -> None:
    """Given a model and a painter get video input from webcam and displays the output to a window"""
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

    outputter = colored_output.ColoredOutput()
    # get requested writer depending on the arguments
    if args.dir and os.path.isdir(args.dir):
        if not args.videoOut:
            print("Argument -o, --videoOut is MISSING")
            exit(-1)
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
