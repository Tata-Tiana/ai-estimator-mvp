# Lintel Concrete Spec Volume

Production-кейс для бетона перемычек из спецификации.

Входной проектный объём:

```text
lintel_concrete_spec_volume_m3 = 1.1
```

В production-режиме коэффициент запаса повторно не применяется:

```text
lintel_required_concrete_volume_m3 = 1.1
lintel_concrete_order_volume_m3 = ceil(1.1) = 2
```
