import argparse
from clip import Clip
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", "-i", help="Path to the input video", type=Path, required=True
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Path to where you want to save the output video. "
             "Note: Not all extensions are supported. Checkout moviepy's documentation",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--magnitude-threshold-ratio",
        "-m",
        help="Audio signal's values ({x in R: -1 <= x <= 1}) that are: "
             "min_magnitude = min(abs(min(x)), max(x))"
             "magnitude_threshold = min_magnitude * magnitude_threshold_ratio"
             "abs(x) < magnitude_threshold"
             "will be threated as silence audio signal values.",
        type=float,
        default=0.02,
    )
    parser.add_argument(
        "--duration-threshold",
        "-d",
        help="Minimum number of required seconds in silence to cut it out",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--failure-tolerance-ratio",
        "-f",
        help="Consequent x values are taken into account to find silence parts of the signal. "
             "Failure tolerance ratio leaves room for some error. For example if failure threshold "
             "ratio is 0.1, then in 1 second silence signal, it is allowed to have 0.1 seconds "
             "non silence signal, and it is still going to be treated as a silence signal.",
        type=float,
        default=0.1,
    )
    parser.add_argument(
        "--space-on-edges",
        "-s",
        help="Leaves some space on the edges of silence cut. E.g. if it is found that there is silence "
             "between 10th and 20th second of the video, then instead of cutting it out directly, "
             "we cut out  (10+space_on_edges)th and (20-space_on_edges)th seconds of the clip",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--silence-part-speed",
        "-x",
        help="If this parameter is set, it will speed up the silence parts x times instead of cutting them out "
             "Then if you want to skip this part set None. ",
        type=int,
        required=False,
        default=1
    )
    parser.add_argument(
        "--min-loud-part-duration",
        "-l",
        help="If this parameter is set, loud parts of the clip that are shorter than this parameter "
             "(in seconds) will also be cutted",
        type=int,
        required=False,
        default=-1,
    )
    parser.add_argument(
        "--codec",
        help="Codec to use for image encoding. Can be any codec supported by ffmpeg. If the filename "
             "has extension ‘.mp4’, ‘.ogv’, ‘.webm’, the codec will be set accordingly, but you can still set "
             "it if you don’t like the default. For other extensions, the output filename must be set accordingly.",
        type=str,
        required=False,
    )
    parser.add_argument(
        "--bitrate",
        help="Desired bitrate for the output video",
        type=int,
        required=False,
    )
    parser.add_argument(
        "--default_img", "-d_",
        help="Path to the inactive status image",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--active_img", "-a_",
        help="Path to the active status image",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--width", "-w_",
        help="Desired width for the output video",
        type=int,
        required=False,
    )
    parser.add_argument(
        "--height", "-h_",
        help="Desired height for the output video",
        type=int,
        required=False,
    )
    parser.add_argument(
        "--fps",
        help="Desired fps for the output video",
        type=int,
        default=None,
    )

    args = parser.parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    default_img = args.default_img.resolve()
    active_img = args.active_img.resolve()

    clip = Clip(str(input_path),
                args.min_loud_part_duration,
                args.silence_part_speed,
                str(default_img),
                str(active_img),
                args.width,
                args.height)
    output = clip.jumpcut(args.magnitude_threshold_ratio,
                          args.duration_threshold,
                          args.failure_tolerance_ratio,
                          args.space_on_edges)
    output.write_videofile(str(output_path), codec=args.codec, bitrate=args.bitrate, fps=args.fps)

if __name__ == '__main__':
    main()