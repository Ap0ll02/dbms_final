# install dependencies

## macos/linux
```bash
python3 -m venv .venv
source .venv/bin/activate

pip install pandas

chmod +x run_queries
```

## windos
if using powershell, uncomment the line below and delete/comment out the one above s
```bash
python3 -m venv .venv
.venv\Scripts\activate # cmd
# .venv\Scripts\Activate.ps1 # powershell

pip install pandas
```

# run:

## macos, linux, wsl
```bash
./run_queries
```

## cmd or powershell
```bash
bash run_queries
```