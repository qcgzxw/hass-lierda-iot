# Refactor 分支 vs Master 分支 代码审查报告

## 概述

本次重构将 `lierda/core/` 和 `lierda/devices/` 目录替换为 [api/](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/models/device.py#23-78) + `models/` + [coordinator.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/coordinator.py) 架构，引入了 HA 标准的 [DataUpdateCoordinator](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/coordinator.py#18-66) 模式。整体方向正确，但存在多个严重 Bug，会导致设备控制和状态读取失败。

---

## 🔴 严重问题（必须修复）

### Bug 1: [set_device_attribute](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/client.py#211-288) 命令协议错误

**文件**: [api/client.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/client.py) 第 238-251 行

```diff
 # 旧版（master）正确格式：
 {
     "sourceId": "123456",          # ← 固定字符串
     "serialNum": int(time()) % 10000,  # ← 时间戳取模，数字
     "requestType": "cmd",          # ← 固定字符串 "cmd"
-    "id": self.macid,              # ← MAC ID（字符串）
-    "ddcId": self.ddcmac,          # ← DDC MAC（字符串）
+    "attributes": attributes       # ← dict，如 {"KY1": "ON"}，直接是dict
 }

 # 新版（refator）错误格式：
 {
     "sourceId": self.auth_data.userid,  # ← 用了 userid（数字），应为 "123456"
     "serialNum": mac_id,                # ← 用了 mac_id（字符串），应为时间戳
     "requestType": "control",          # ← 写成了 "control"，应为 "cmd"
     "id": device_id,                    # ← 用了 device_id（整数），应为 macid（字符串）
     "ddcId": ddc_mac,                   # ← 正确
-    "attributes": [{attribute: value}]  # ← 用了列表包dict，应为直接 dict
 }
```

此 Bug 会导致所有控制命令（开关、灯、窗帘）发往服务端后无法被识别，**所有控制功能完全失效**。

**正确写法应为**：
```python
cmd_str = json.dumps({
    "sourceId": "123456",
    "serialNum": int(time.time()) % 10000,
    "requestType": "cmd",
    "id": mac_id,           # MAC ID 字符串
    "ddcId": ddc_mac,
    "attributes": {attribute: value},  # 直接是 dict，不是列表
})
```

---

### Bug 2: [get_all_devices](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/client.py#141-210) 请求体缺少字段，且 `role` 字段传错

**文件**: [api/client.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/client.py) 第 157-166 行

```diff
 request_data = {
     "pn": "getDeviceListByUserId",
     "userid": self.auth_data.userid,
-    "uid": self.auth_data.userid,
-    "role": self.auth_data.role,         # ← 旧版 master 传的是 userid，不是 role
+    "role": self.auth_data.userid,       # ← 应该传 userid（参照 master 源码）
     "ibmsuserid": self.auth_data.userid,
     "ibmsuserole": self.auth_data.role,
     "ibmsparentid": self.auth_data.parentid,
     "ibmsnat": self.auth_data.nat,
 }
```

> 参照 master 分支 `LierdaApi.get_device_list_by_user_id()`:
> ```python
> async def get_device_list_by_user_id(self):
>     return await self.action(ACTION_GET_DEVICE_LIST_BY_USER_ID, {
>         "uid": self.userid,
>         "role": self.userid,   # ← role 字段传的是 userid
>     })
> ```

---

### Bug 3: Switch 开关状态读取错误（[is_on](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/binary_sensor.py#84-92) 逻辑）

**文件**: [switch.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/switch.py) 第 86-96 行

新版代码直接用 `entity_key.upper()`（如 `"KY1"`）读取 attributes，然后与字符串 `"ON"` 对比：

```python
value = device.get_attribute(attribute_name)   # "KY1" -> 可能是 None
if value:
    return value == "ON"
```

但 master 分支的 `LierdaSwitchDevice.is_on()` 表明：开关状态实际上存储在 `SWI`（一个十六进制值），需要通过**位运算**计算各路开关状态：

```python
# master 正确逻辑：
swi = int(self.get_attribute("SWI"), 16)  # 如 "0x03" -> 3
index = int(attr.removeprefix("ky"))      # "ky1" -> 1
light_mask = 1 << (index - 1)            # 1 << 0 = 1
return (swi & light_mask) != 0           # 检查对应位
```

新版代码假设 API 直接返回 `KY1=ON/OFF`，**这与实际 API 协议不符**，会导致所有开关状态始终为 `False`。

---

### Bug 4: `binary_sensor` 门磁状态读取使用了错误的 `entity_key`

**文件**: [binary_sensor.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/binary_sensor.py) 第 84-91 行

```python
# 新版（错误）
return bool(device.get_attribute(self.entity_key))  # entity_key = "door"
```

但 lierda_devices.py 中 entity_key 是 `"door"`（小写），而实际 API 返回的属性键是 `"WIN"`（window） 或其他。

参照 master 的 `LierdaDoorDevice`，门磁用 `DOR`（或类似大写键），判断是否 `== "OPEN"`：
```python
return self.entry_get_attribute(DeviceAttributes.door) == "OPEN"
```

新版代码没有完成 entity_key → 实际 API 属性键的映射，**门磁状态永远读不到正确值**。

---

### Bug 5: `sensor` 电池传感器 `entity_key` 无法映射到实际 API 属性键

**文件**: [sensor.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/sensor.py) 第 86-93 行

```python
return device.get_attribute(self.entity_key)   # entity_key = "battery_voltage" 或 "battery_percentage"
```

Master 分支中，这些属性的真实 API 键是 `BAV`（电压）和 `BAP`（电量百分比）等，并且电量百分比需要去掉 `%` 后缀：

```python
# master 正确：
return int(self.entry_get_attribute(DeviceAttributes.battery_percentage).removesuffix("%"))
```

新版代码直接用可读名字查属性字典，**实际上永远返回 `None`**。

---

## 🟡 中等问题（影响稳定性）

### Bug 6: [LierdaDataUpdateCoordinator](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/coordinator.py#18-66) 不处理连接错误

**文件**: [coordinator.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/coordinator.py) 第 62-65 行

```python
except LierdaApiError as err:
    raise UpdateFailed(...)
```

[LierdaConnectionError](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/exceptions.py#17-19) 和 [LierdaTimeoutError](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/exceptions.py#21-23) 继承自 [LierdaApiError](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/exceptions.py#9-11)，所以它们会被捕获，这部分 OK。但 [_request()](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/client.py#47-78) 在非 200 响应时抛的是 [LierdaConnectionError](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/exceptions.py#17-19)，也在捕获范围内。不过如果 `aiohttp` 抛出未预期的 `Exception`，coordinator 会崩溃，建议加宽捕获：

```python
except Exception as err:
    raise UpdateFailed(f"Unexpected error: {err}") from err
```

---

### Bug 7: [config_flow.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/config_flow.py) 的 [async_step_init](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/config_flow.py#251-270)（Options Flow）仍在引用旧的数据结构

**文件**: [config_flow.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/config_flow.py) 第 261 行

```python
for device_id, device in self.hass.data[DOMAIN][LIERDA_DEVICES].items():
    device.set_refresh_interval(refresh_interval)
```

`LIERDA_DEVICES` 现在是 [lierda_devices.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/lierda_devices.py) 里的一个 dict 常量（不再是 `hass.data` 里的 key），且新版设备对象是 [Device](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/models/device.py#8-104) dataclass，**没有 `set_refresh_interval` 方法**。这段代码会在 Options Flow 执行时抛出 `KeyError` / `AttributeError`。同时 coordinator 的刷新间隔在 options flow 中也没有被更新。

---

### Bug 8: [coordinator.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/coordinator.py) 和 [client.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/client.py) 使用绝对 import 路径

**文件**: [api/client.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/client.py) 第 11-18 行, [coordinator.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/coordinator.py) 第 11-13 行

```python
from custom_components.lierda_iot.api.exceptions import ...
from custom_components.lierda_iot.models.device import Device
```

Home Assistant 自定义组件应使用**相对 import**，否则在某些 HA 安装环境下（如 HACS）可能找不到模块：

```python
from .exceptions import ...      # 在 api/ 内部
from ..models.device import Device
```

---

### Bug 9: [lierda_devices.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/lierda_devices.py) 缺失部分设备类型

对比 master 分支 `lierda/devices/__init__.py`，新版 [lierda_devices.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/lierda_devices.py) 漏掉了以下设备类型：

| 设备代码 | 类型值 | 描述 |
|---|---|---|
| `TYPE_LT_CTM` | 1 | 另一种灯 |
| `TYPE_SW_TK2/3/4` | 2, 3, 4 | TK 系列开关 |
| `TYPE_WD_DYK` | 6 | 另一种窗帘 |
| `TYPE_DL_LCK` | 11 | 门锁 |

这些设备在 [const.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/const.py) 中也没有定义，会被静默跳过。

---

### Bug 10: [cover.py](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/cover.py) 中遮帘属性键使用错误名称

**文件**: [cover.py](file:///home/owen/文档/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/cover.py) 第 91, 105, 119 行

```python
if device.get_attribute("window") is not None:   # 应为 "WIN"
    window = device.get_attribute("window")       # 应为 "WIN"
    level = device.get_attribute("level")         # 应为 "LEV"
```

根据 master 的 `LierdaCurtainDevice`，实际 API 返回的属性键是 `WIN` 和 `LEV`，不是小写的 `window` / `level`，导致窗帘状态始终读取失败，功能特性也无法被正确检测。

---

## 🟢 正确/改进之处

- ✅ 引入 [DataUpdateCoordinator](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/coordinator.py#18-66) 是 HA 最佳实践，替代了旧版自行维护 Thread 的危险方式
- ✅ [Device](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/models/device.py#8-104) dataclass 和 [AuthData](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/models/auth.py#6-43) dataclass 结构清晰简洁  
- ✅ 异常层次结构（[LierdaError](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/exceptions.py#5-7) → [LierdaApiError](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/api/exceptions.py#9-11) → ...）划分合理
- ✅ [async_migrate_entry](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/__init__.py#34-93) 向下兼容 v1/v2 的迁移逻辑完整
- ✅ coordinator 复用同一个 `aiohttp.ClientSession`（持久化 session），比旧版每次请求新建 session 更高效
- ✅ 各平台的 [device_info](file:///home/owen/%E6%96%87%E6%A1%A3/github/qcgzxw/hass-lierda-iot/custom_components/lierda_iot/binary_sensor.py#93-103) 返回格式统一
- ✅ 平台代码结构统一，便于维护

---

## 修复优先级

| 优先级 | Bug | 影响 |
|---|---|---|
| P0 | Bug 1: cmd 协议错误 | 所有控制命令失效 |
| P0 | Bug 3: Switch is_on 位运算缺失 | 所有开关状态错误 |
| P0 | Bug 4/5: 传感器键名错误 | 门磁/电池传感器永远为空 |
| P0 | Bug 10: 窗帘键名错误 | 窗帘状态读取失败 |
| P1 | Bug 2: get_all_devices role 字段 | 可能导致设备列表获取失败 |
| P1 | Bug 7: Options Flow 崩溃 | 修改刷新间隔时报错 |
| P2 | Bug 8: 绝对 import | 环境兼容性问题 |
| P2 | Bug 6: coordinator 异常处理 | 边缘情况下崩溃 |
| P3 | Bug 9: 缺失设备类型 | 部分设备无法接入 |
