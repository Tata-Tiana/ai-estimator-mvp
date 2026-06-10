# Main Walls Crane From Delivery Trucks Four

Production-кейс для верхнего порога правила Елены по крану несущих стен:

```text
if gas_block_delivery_trucks <= 3:
    main_walls_crane_shifts = 1
else:
    main_walls_crane_shifts = 2
```

В этом кейсе вместимость машины блоков задана так, чтобы получилось 4 доставки. Поле `main_walls_crane_shifts` не передаётся вручную.
