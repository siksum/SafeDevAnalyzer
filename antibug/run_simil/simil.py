import logging
import operator
import sys
import traceback
from argparse import Namespace
import os

from join.compile.compile import Join
from join.run_simil.cache import save_cache
from join.run_simil.encode import encode_contract, load_contracts, parse_target, load_and_encode
from join.run_simil.model import train_unsupervised, load_model
from join.run_simil.similarity import similarity

logger = logging.getLogger("Slither-simil")
logger.setLevel(logging.INFO)  # Set log level to INFO


class Simil:
    @staticmethod
    def test(path, fname, detector, bin) -> list:
        result = []
        args = Namespace(mode='test', model=bin, filename=path,
                         fname=fname, ntop=10, input=detector)
        try:
            model = args.model
            model = load_model(model)
            filename = args.filename
            contract, fname = parse_target(args.fname)
            infile = args.input
            ntop = args.ntop

            if filename is None or contract is None or fname is None or infile is None:
                print(
                    "The test mode requires filename, contract, fname and input parameters.")
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
            for x, score in r[:ntop]:
                score = round(score, 3)
                result.append(list(x) + [score])
            return result

        except Exception as e:
            print(f"Error in {args.filename}")
            print(traceback.format_exc())
            sys.exit(-1)

    @staticmethod
    def train(bin, contract):
        args = Namespace(mode='train', model=bin,
                         input=contract, filename=None)

        try:
            last_data_train_filename = os.path.join(
                os.path.dirname(__file__), "last_data_train.txt")
            model_filename = args.model
            dirname = args.input
            if dirname is None:
                logger.error("The train mode requires the input parameter.")
                sys.exit(-1)
            contracts = load_contracts(dirname)
            logger.info("Saving extracted data into %s",
                        last_data_train_filename)
            cache = []
            with open(last_data_train_filename, "w", encoding="utf8") as f:
                for filename in contracts:
                    r = encode_contract(filename, **vars(args))
                    for (filename_inner, contract, function), ir in encode_contract(
                        filename, **vars(args)
                    ).items():
                        if ir != []:
                            x = " ".join(ir)
                            f.write(x + "\n")
                            cache.append(
                                (os.path.split(filename_inner)[-1], contract, function, x))
            logger.info("Starting training")
            model = train_unsupervised(
                input=last_data_train_filename, model="skipgram")
            logger.info("Training complete")
            logger.info("Saving model")
            model.save_model(model_filename)

            for i, (filename, contract, function, irs) in enumerate(cache):
                cache[i] = ((filename, contract, function),
                            model.get_sentence_vector(irs))

            logger.info("Saving cache in cache.npz")
            save_cache(cache, "cache.npz")
            logger.info("Done!")

        except Exception:  # pylint: disable=broad-except
            logger.error(f"Error in {args.filename}")
            logger.error(traceback.format_exc())
            sys.exit(-1)

    def _check_similar(self, path, detector, contract):
        compile = Join(path)
        detector_path = os.path.join(
            os.path.dirname(__file__), "Category", detector)
        path = compile.target_path
        bin_path = os.path.join(os.path.dirname(
            __file__), "etherscan_verified_contracts.bin")
        functions = []
        for compilation_unit in compile.compilation_units.values():
            for unit in compilation_unit.compilation_units:
                for con in unit.contracts:
                    if str(con) == str(contract):
                        for function in con.functions:
                            if function.expressions:
                                functions.append(function.name)

        result = []

        for func in functions:
            fname = f'{contract}.{func}'
            results = self.test(path, fname, detector_path, bin_path)
            for r in results:
                if r[3] > 0.95:
                    result.append(
                        {'function': func, "detect": r[1]+"."+r[2], 'detector': r[2], 'score': r[3], 'fname': fname})
                else:
                    pass
        return result

# simil = Simil()

# def test(path, fname, detector, bin)
# test = simil.test('uni.sol', 'Router.Hi', 'Uniswap')
# [print(t) for t in test]

# def train(bin, contract):
# train = simil.train('model.bin', 'Uniswap')

# simil = Simil()
# detect = simil._check_similar('/Users/dlanara/Desktop/immm/code/category/uniswapv2/uniswapv2.sol', 'Uniswap', '/Users/dlanara/Desktop/immm/backup/Uniswap')
