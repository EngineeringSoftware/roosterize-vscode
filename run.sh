#!/bin/bash

_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )


function process_data() {
        ( cd $_DIR/python/
          python -m roosterize.main extract_data_from_corpus\
                 --corpus=$_DIR/../math-comp-corpus\
                 --output=$_DIR/output/data\
                 --groups=ta
        )
}

function train() {
        ( cd $_DIR/python/
          rm -rf output/model
          python -m roosterize.main train_model\
                 --train=$_DIR/output/data/ta-train\
                 --val=$_DIR/output/data/ta-val\
                 --model-dir=$_DIR/output/model\
                 --output=$_DIR/output/data\
                 --config-file=$_DIR/configs/Stmt+ChopKnlTree+attn+copy.json
        )
}

function eval() {
        ( cd $_DIR/python/
          python -m roosterize.main eval_model\
                 --data=$_DIR/output/data/ta-test\
                 --model-dir=$_DIR/output/model\
                 --output=$_DIR/output/results
        )
}


# ==========
# Main function -- program entry point
# This script can be executed as ./run.sh the_function_to_run

function main() {
        local action=${1:?Need Argument}; shift

        ( cd ${_DIR}
          $action "$@"
        )
}

main "$@"

