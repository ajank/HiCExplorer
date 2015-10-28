import sys, argparse
import numpy as np
from scipy.sparse import lil_matrix, vstack, triu
from hicexplorer import HiCMatrix as hm
from hicexplorer._version import __version__


def parse_arguments(args=None):
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=('Adds Hi-C matrices of the same size. Format '
                                                  'has to be .npz.'))

    parser.add_argument('--matrices', '-m',
                        help='matrices to add. Must have the same shape.',
                        metavar='.npz file format',
                        nargs='+',
                        required=True)

    parser.add_argument('--outFileName', '-o',
                        help='File name to save the resulting matrix. The output is '
                             'also a .npz file. But don\'t add the suffix',
                        required=True)

    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))

    return parser


def main():
    
    args = parse_arguments().parse_args()
    hic = hm.hiCMatrix(args.matrices[0])
    summed_matrix = hic.matrix
    nan_bins = set(hic.nan_bins)
    for matrix in args.matrices[1:]:
        try:
            _loaded_data = np.load(matrix)
        except:
            print "\nMatrix {} seems to be empty.".format(matrix)
            exit(1)

        try:
            summed_matrix = summed_matrix + _loaded_data['matrix'].tolist()
            if 'nan_bins' in _loaded_data:
                nan_bins = nan_bins.union(_loaded_data['nan_bins'])
        except:
            print "\nMatrix {} seems to be corrupted or of different " \
                  "shape".format(matrix)
            exit(1)

    # save only the upper triangle of the
    # symmetric matrix
    hic.setMatrixValues(summed_matrix)
    hic.maskBins(sorted(nan_bins))
    hic.save(args.outFileName)
