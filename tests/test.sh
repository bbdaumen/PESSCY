#!bin/bash

cd "$(dirname "$0")"

### Generation tests

echo "Generate Anemoi equations"
pesscy generate -o anemoi -p anemoi -b 2 -r 2 -f 443 -c 1 -n 2
tail -n 1 "../results/generate/anemoi/anemoi.log"
pesscy read -m 'generate' -f anemoi
echo ""

echo "Generate Anemoiround equations"
pesscy generate -o anemoiround -p anemoiround -b 2 -r 2 -f 443 -c 1
tail -n 1 "../results/generate/anemoiround/anemoiround.log"
pesscy read -m 'generate' -f anemoiround
echo ""

echo "Generate Griffin equations"
pesscy generate -o griffin -p griffin -b 3 -r 1 -f 11 -c 1
tail -n 1 "../results/generate/griffin/griffin.log"
pesscy read -m 'generate' -f griffin
echo ""

echo "Generate Zerolith equations"
pesscy generate -o zerolith -p zerolith -b 4 -r 2 -f 443 -c 2
tail -n 1 "../results/generate/zerolith/zerolith.log"
pesscy read -m 'generate' -f zerolith
echo ""

### Attack tests

echo "Solve Anemoi equations"
pesscy solve -o anemoi -g singular:groebner -i anemoi -o anemoi -tc 50
tail -n 1 "../results/solve/anemoi/anemoi.log"
pesscy read -m 'solve' -f anemoi
echo ""

echo "Solve Anemoiround equations"
pesscy solve -o anemoiround -g singular:std -i anemoiround -o anemoiround -oc fglm -tc 50
tail -n 1 "../results/solve/anemoiround/anemoiround.log"
pesscy read -m 'solve' -f anemoiround
echo ""

echo "Solve Griffin equations"
pesscy solve -o griffin -g singular:slimgb -i griffin -o griffin -oc gwalk -tc 50
tail -n 1 "../results/solve/griffin/griffin.log"
pesscy read -m 'solve' -f griffin
echo ""

echo "Solve Zerolith equations"
pesscy solve -o zerolith -g singular:stdhilb -i zerolith -o zerolith -oc twalk -tc 50
tail -n 1 "../results/solve/zerolith/zerolith.log"
pesscy read -m 'solve' -f zerolith
echo ""

### Benchmark tests

echo "Benchmark Anemoi"
pesscy benchmark -p anemoi -c 0 -s 0
tail -n 1 "../results/benchmark/anemoi_set_0_0/logs/1.log"
tail -n 1 "../results/benchmark/anemoi_set_0_0/logs/global.log"
echo ""

echo "Benchmark Zerolith"
pesscy benchmark -p zerolith -c 0 -s 0
tail -n 1 "../results/benchmark/zerolith_set_0_0/logs/1.log"
tail -n 1 "../results/benchmark/zerolith_set_0_0/logs/global.log"
echo ""

### Comparison random tests

echo "Comparison Anemoi"
pesscy random_comparison -c 0
tail -n 1 "../results/comparisons/random_compare_anemoi_set_0_0/logs/1.log"
tail -n 1 "../results/comparisons/random_compare_anemoi_set_0_0/logs/global.log"

echo ""

echo "Comparison Zerolith"
pesscy random_comparison -c 3
tail -n 1 "../results/comparisons/random_compare_zerolith_set_0_0/logs/1.log"
tail -n 1 "../results/comparisons/random_compare_zerolith_set_0_0/logs/global.log"