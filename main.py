import argparse
from ModelWrapper import Wrapper

modello=[".\\mpi\\pose_iter_160000.caffemodel",".\\mpi\\pose_deploy_linevec_faster_4_stages.prototxt"]

def main():
    parser = argparse.ArgumentParser(description='Process images')
    parser.add_argument("--videoIn","-i",type=str, default="0" ,help="input file")
    parser.add_argument("--videoOut","-o",type=str,help="file di output opzionale")
    parser.add_argument("-m",default=False, action="store_true")
    args=parser.parse_args()
    wrapper=Wrapper(args.videoIn,modello[0],modello[1],args.videoOut,args.m)
    wrapper.run_simulation()

if __name__=="__main__":
    main()