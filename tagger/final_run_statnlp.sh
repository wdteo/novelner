OMP_NUM_THREADS=10 python ./train.py --model_path ./models/all_5055_adam --train ../final_data/train.final.featured --dev ../final_data/dev.final.featured.new --test ../final_data/test.final.featured.new.labeled --pre_emb /home/yuchen/useful_data/glove.twitter.27B.100d.txt --zeros 1 --pos_dim 5 --dep_dim 0 --ind_dim 5 --head_dim 5 --word_dim 100 --word_lstm_dim 100 --lr_method adam
# test data will not be used 
