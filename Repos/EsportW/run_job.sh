DIR=$(readlink -f $(dirname $0))
LOG=$DIR/logs/scripts
mkdir -p $LOG
log_file=$LOG/$(date +%m%d-%H%M).log
touch $log_file

cd $DIR
echo $(PWD)
source ~/.zshrc
conda activate lol


if [ -z "$1" ]; then
    sleep_time=$((RANDOM % 1200))
else 
    sleep_time=$1
fi

echo "Simulating operation, random sleep $(($sleep_time / 60)) minutes" | tee -a $log_file
sleep $sleep_time
echo "Starting the program\n" | tee -a $log_file

python -u "/Users/ove/Development/python/lol-epsort/EsportsHelper/main.py" | tee -a $log_file  
