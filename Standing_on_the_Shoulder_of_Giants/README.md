#  Standing on the Shoulder of Giants

## Create Environment

`$ conda create -n ziplive python=3.6`

`$ conda activate ziplive`

## Packages

Install [pylivetrader](https://github.com/alpacahq/pylivetrader)

`$ pip install pylivetrader`

Install the [python wrapper](https://github.com/mrjbq7/ta-lib) for [TA-Lib](https://www.ta-lib.org/)

`$ pip install TA-Lib`

Install [scikit-learn](https://scikit-learn.org/stable/) 

`$ pip install scikit-learn==0.23.2`

Install [ipykernel](https://ipython.org/)

`$ pip install ipykernel`

Install [graphviz](https://pypi.org/project/graphviz/0.19.1/)

`$ pip install graphviz==0.19.1`

Configuration by config file *config.yaml*

`$ cat config.yaml`

`key_id: {your api key id}`

`secret: {your api secret key}`

`base_url: {https://api.alpaca.markets/ or https://paper-api.alpaca.markets}`


## Run the Strategy 

to trade with pipeline-live you need to export the config data and then run the algo.

`export APCA_API_KEY_ID="api_key"`
`export APCA_API_SECRET_KEY="api_secret_key"`
`export APCA_API_BASE_URL=https://paper-api.alpaca.markets`


`$ pylivetrader run -f long_short_pipeline_algoo.py`
