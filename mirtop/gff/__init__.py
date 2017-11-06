import os.path as op

from mirtop.mirna import fasta, mapper
from mirtop.bam.bam import read_bam
from mirtop.importer import seqbuster, srnabench, prost
from mirtop.mirna.annotate import annotate
from mirtop.gff import body, header
import mirtop.libs.logger as mylog
logger = mylog.getLogger(__name__)

def reader(args):
    """
    Realign BAM hits to miRBAse to get better accuracy and annotation
    """
    database = mapper.guess_database(args.gtf)
    # hairpin, mirna = download_mirbase(args)
    precursors = fasta.read_precursor(args.hairpin, args.sps)
    matures = mapper.read_gtf_to_precursor(args.gtf)
    # check numnbers of miRNA and precursors read
    # print message if numbers mismatch
    out_dts = dict()
    for fn in args.files:
        sample = op.splitext(op.basename(fn))[0]
        fn_out = op.join(args.out, sample + ".gff")
        if args.format == "BAM":
            reads = _read_bam(fn, precursors)
        elif args.format == "seqbuster":
            reads = seqbuster.read_file(fn, precursors)
            custom = seqbuster.header()
        elif args.format == "srnabench":
            reads = srnabench.read_file(fn, precursors)
        elif args.format == "prost":
            reads = prost.read_file(fn, precursors, args.gtf)
        h = header.create([sample], database, "")
        ann = annotate(reads, matures, precursors)
        out_dts[fn] = body.create(ann, database, sample)
        _write(out_dts[fn], h, fn_out)
    # merge all reads for all samples into one dicts
    # from dict with all samples convert each in a gff line

def _write(lines, headder, fn):
    out_handle = open(fn, 'w')
    print >>out_handle, header
    for m in lines:
        print >>out_handle, lines[m][4]
    out_handle.close()

def _read_bam(bam_fn, precursors):
    if bam_fn.endswith("bam") or bam_fn.endswith("sam"):
        logger.info("Reading %s" % bam_fn)
        reads = read_bam(bam_fn, precursors)
    else:
        raise ValueError("Format not recognized. Only working with BAM/SAM files.")
    return reads
