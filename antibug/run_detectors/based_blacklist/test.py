import logging
import operator
import sys
import traceback
from argparse import Namespace

from antibug.run_detectors.based_blacklist.encode import encode_contract, load_and_encode, parse_target
from antibug.run_detectors.based_blacklist.model import load_model
from antibug.run_detectors.based_blacklist.similarity import similarity

logger = logging.getLogger("Slither-simil")


def test(path, fname, input, bin) -> list:
    args = Namespace(mode='test', model=bin, filename=path,
                        fname=fname, ntop=10, input=input)
    try:
        model = args.model
        model = load_model(model)
        filename = args.filename
        contract, fname = parse_target(args.fname)
        infile = args.input
        ntop = args.ntop


        if filename is None or contract is None or fname is None or infile is None:
            logger.error("The test mode requires filename, contract, fname and input parameters.")
            sys.exit(-1)

        irs = encode_contract(filename, **vars(args))
        if len(irs) == 0:
            sys.exit(-1)

        y = " ".join(irs[(filename, contract, fname)])
        fvector = model.get_sentence_vector(y)

        cache = load_and_encode(infile, model, **vars(args))

        # save_cache("cache.npz", cache)
        r = {}
        for x, y in cache.items():
            r[x] = similarity(fvector, y)

        r = sorted(r.items(), key=operator.itemgetter(1), reverse=True)

        logger.info("Reviewed %d functions, listing the %d most similar ones:", len(r), ntop)
        format_table = "{: <65} {: <20} {: <20} {: <10}"
        logger.info(format_table.format(*["filename", "contract", "function", "score"]))
        result = {}
        for x, score in r[:ntop]:
            score = str(round(score, 3))
            result[x] = score

            # logger.info(format_table.format(*(list(x) + [score])))
        return filename, contract, fname, result


    except Exception:  # pylint: disable=broad-except
        logger.error(f"Error in {args.filename}")
        logger.error(traceback.format_exc())
        sys.exit(-1)
