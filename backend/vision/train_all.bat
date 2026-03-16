@echo off

echo =========================================
echo  Mahjong Tile Classifier - Full Training
echo =========================================
echo.

echo [1/9] Layer 1 - Group classifier
python train_model.py --layer 1 --type group
echo.

echo [2/9] Layer 2 - Suit type (char/bam/dot)
python train_model.py --layer 2 --type suit_type
echo.

echo [3/9] Layer 2 - Honor type (wind/dragon)
python train_model.py --layer 2 --type honor_type
echo.

echo [4/9] Layer 2 - Bonus type (animal/flower)
python train_model.py --layer 2 --type bonus_type
echo.

echo [5/9] Layer 3 - Char (1-9) [100 epochs]
python train_model.py --layer 3 --type char --epochs 100
echo.

echo [6/9] Layer 3 - Bam (1-9)
python train_model.py --layer 3 --type bam
echo.

echo [7/9] Layer 3 - Dot (1-9) [100 epochs]
python train_model.py --layer 3 --type dot --epochs 100
echo.

echo [8/9] Layer 3 - Wind (EAST/SOUTH/WEST/NORTH) [100 epochs]
python train_model.py --layer 3 --type wind --epochs 100
echo.

echo [9/9] Layer 3 - Dragon (RED/GREEN/WHITE)
python train_model.py --layer 3 --type dragon
echo.

echo =========================================
echo  All models trained successfully!
echo =========================================

:end