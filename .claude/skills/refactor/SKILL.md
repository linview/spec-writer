---
name: refactor
description: 安全重构代码技能。当用户提到"重构"、"改进代码"、"代码异味"、"清理代码"、"优化结构"或需要改善代码质量时使用。
---

# 安全重构

## 使用说明

### 自动触发场景

本 skill 会在以下情况自动激活：
- 用户要求重构代码
- 用户提到"代码异味"、"代码质量"或"改进代码"
- 用户请求清理或优化代码结构
- 在 TDD 循环的 Refactor 阶段
- 代码审查中发现需要改进的地方

### 核心原则

**重构不改变外部行为，只改进内部结构。测试必须始终通过。**

## 何时重构

### 在 TDD 循环中
- 每个 Red-Green 循环后都应检查是否需要重构
- 不要等到代码"完全烂掉"才重构
- 小步重构，频繁重构

### 重构信号（Code Smells）

#### 1. 重复代码

```go
// ❌ 代码异味：重复逻辑
func ValidateUserEmail(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    return nil
}

func ValidateAdminEmail(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    // 额外的验证...
    return nil
}

// ✓ 重构后：提取公共函数
func validateEmailFormat(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    return nil
}

func ValidateUserEmail(email string) error {
    return validateEmailFormat(email)
}

func ValidateAdminEmail(email string) error {
    if err := validateEmailFormat(email); err != nil {
        return err
    }
    // 额外的验证...
    return nil
}
```

#### 2. 函数过长

```go
// ❌ 代码异味：函数过长（超过 20-30 行）
func RegisterUser(email, password string) (*User, error) {
    // 验证邮箱
    if email == "" {
        return nil, errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return nil, errors.New("邮箱格式无效")
    }

    // 验证密码
    if len(password) < 8 {
        return nil, errors.New("密码过短")
    }
    hasLetter := false
    hasDigit := false
    for _, c := range password {
        if unicode.IsLetter(c) {
            hasLetter = true
        }
        if unicode.IsDigit(c) {
            hasDigit = true
        }
    }
    if !hasLetter || !hasDigit {
        return nil, errors.New("密码必须包含字母和数字")
    }

    // 检查邮箱是否已存在
    // ... 更多逻辑

    // 创建用户
    // ... 更多逻辑

    return user, nil
}

// ✓ 重构后：提取小函数
func RegisterUser(email, password string) (*User, error) {
    if err := validateEmail(email); err != nil {
        return nil, err
    }

    if err := validatePassword(password); err != nil {
        return nil, err
    }

    if err := checkEmailUniqueness(email); err != nil {
        return nil, err
    }

    return createUser(email, password)
}

func validateEmail(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    return nil
}

func validatePassword(password string) error {
    if len(password) < 8 {
        return errors.New("密码过短")
    }

    hasLetter := regexp.MustCompile(`[a-zA-Z]`).MatchString(password)
    hasDigit := regexp.MustCompile(`[0-9]`).MatchString(password)

    if !hasLetter || !hasDigit {
        return errors.New("密码必须包含字母和数字")
    }

    return nil
}
```

#### 3. 魔法数字/字符串

```go
// ❌ 代码异味：魔法数字
func ValidatePassword(password string) error {
    if len(password) < 8 {
        return errors.New("密码过短")
    }
    if len(password) > 128 {
        return errors.New("密码过长")
    }
    return nil
}

// ✓ 重构后：使用命名常量
const (
    MinPasswordLength = 8
    MaxPasswordLength = 128
)

func ValidatePassword(password string) error {
    if len(password) < MinPasswordLength {
        return fmt.Errorf("密码至少需要 %d 个字符", MinPasswordLength)
    }
    if len(password) > MaxPasswordLength {
        return fmt.Errorf("密码最多 %d 个字符", MaxPasswordLength)
    }
    return nil
}
```

#### 4. 过多的参数

```go
// ❌ 代码异味：参数过多
func CreateUser(email, password, firstName, lastName, phone, address, city, country, zipCode string) (*User, error) {
    // ...
}

// ✓ 重构后：使用结构体
type UserRegistration struct {
    Email     string
    Password  string
    FirstName string
    LastName  string
    Phone     string
    Address   string
    City      string
    Country   string
    ZipCode   string
}

func CreateUser(reg UserRegistration) (*User, error) {
    // ...
}
```

#### 5. 深层嵌套

```go
// ❌ 代码异味：深层嵌套
func ProcessUser(user *User) error {
    if user != nil {
        if user.Email != "" {
            if isValidEmail(user.Email) {
                if !emailExists(user.Email) {
                    // 实际逻辑
                    return save(user)
                } else {
                    return errors.New("邮箱已存在")
                }
            } else {
                return errors.New("邮箱无效")
            }
        } else {
            return errors.New("邮箱为空")
        }
    } else {
        return errors.New("用户为 nil")
    }
}

// ✓ 重构后：早返回（Guard Clauses）
func ProcessUser(user *User) error {
    if user == nil {
        return errors.New("用户为 nil")
    }

    if user.Email == "" {
        return errors.New("邮箱为空")
    }

    if !isValidEmail(user.Email) {
        return errors.New("邮箱无效")
    }

    if emailExists(user.Email) {
        return errors.New("邮箱已存在")
    }

    return save(user)
}
```

## 重构技术

### 1. 提取函数（Extract Function）

当一段代码可以被组织在一起并独立命名：

```go
// 重构前
func PrintOwing(invoice *Invoice) {
    printBanner()

    // 计算未付款金额
    outstanding := 0.0
    for _, order := range invoice.Orders {
        outstanding += order.Amount
    }

    // 打印详情
    fmt.Printf("客户: %s\n", invoice.Customer)
    fmt.Printf("未付金额: %.2f\n", outstanding)
}

// 重构后
func PrintOwing(invoice *Invoice) {
    printBanner()
    outstanding := calculateOutstanding(invoice)
    printDetails(invoice, outstanding)
}

func calculateOutstanding(invoice *Invoice) float64 {
    outstanding := 0.0
    for _, order := range invoice.Orders {
        outstanding += order.Amount
    }
    return outstanding
}

func printDetails(invoice *Invoice, outstanding float64) {
    fmt.Printf("客户: %s\n", invoice.Customer)
    fmt.Printf("未付金额: %.2f\n", outstanding)
}
```

### 2. 内联函数（Inline Function）

当函数体和函数名一样清晰时：

```go
// 重构前
func getRating(driver *Driver) int {
    return moreThanFiveLateDeliveries(driver) ? 2 : 1
}

func moreThanFiveLateDeliveries(driver *Driver) bool {
    return driver.NumberOfLateDeliveries > 5
}

// 重构后（函数名没有增加额外价值）
func getRating(driver *Driver) int {
    return driver.NumberOfLateDeliveries > 5 ? 2 : 1
}
```

### 3. 提取变量（Extract Variable）

当表达式难以理解时：

```go
// 重构前
func Price(order *Order) float64 {
    return order.Quantity*order.ItemPrice -
        max(0, order.Quantity-500)*order.ItemPrice*0.05 +
        min(order.Quantity*order.ItemPrice*0.1, 100)
}

// 重构后
func Price(order *Order) float64 {
    basePrice := order.Quantity * order.ItemPrice
    quantityDiscount := max(0, order.Quantity-500) * order.ItemPrice * 0.05
    shipping := min(basePrice*0.1, 100)
    return basePrice - quantityDiscount + shipping
}
```

### 4. 重命名（Rename Variable/Function）

改善命名以提高可读性：

```go
// 重构前
func calc(u *User) float64 {
    var t float64
    for _, o := range u.Orders {
        t += o.Amount
    }
    return t
}

// 重构后
func calculateTotalOrderAmount(user *User) float64 {
    totalAmount := 0.0
    for _, order := range user.Orders {
        totalAmount += order.Amount
    }
    return totalAmount
}
```

### 5. 引入参数对象（Introduce Parameter Object）

多个参数经常一起出现：

```go
// 重构前
func CreateInvoice(customerName, customerEmail, customerPhone string,
                   amount float64, dueDate time.Time) *Invoice {
    // ...
}

// 重构后
type Customer struct {
    Name  string
    Email string
    Phone string
}

func CreateInvoice(customer Customer, amount float64, dueDate time.Time) *Invoice {
    // ...
}
```

## 重构流程

### 标准重构步骤

#### 1. 确保测试通过

```bash
go test ./... -v
```

所有测试必须是绿色的才能开始重构

#### 2. 进行小的重构

- 一次只做一个小改动
- 例如：只重命名一个变量，或只提取一个函数

#### 3. 运行测试

```bash
go test ./... -v
```

确保重构没有破坏功能

#### 4. 提交（可选）

```bash
git add .
git commit -m "重构: 提取 validateEmail 函数"
```

#### 5. 重复步骤 2-4

继续下一个小的重构

### 重构检查清单

每次重构后检查：

- [ ] 所有测试都通过
- [ ] 代码更易读
- [ ] 没有引入新的复杂性
- [ ] 没有改变外部行为
- [ ] 函数/变量命名更清晰
- [ ] 消除了重复代码
- [ ] 降低了耦合度

## 重构原则

### DO（应该做）

✓ **小步重构** - 每次只改一个地方
✓ **频繁测试** - 每次改动后都运行测试
✓ **保持绿灯** - 重构过程中测试必须始终通过
✓ **改善命名** - 好的命名是最好的文档
✓ **消除重复** - DRY (Don't Repeat Yourself)
✓ **简化逻辑** - 能用简单方法就不用复杂方法

### DON'T（不应该做）

✗ **不要同时重构和添加功能** - 一次只做一件事
✗ **不要在红灯时重构** - 测试失败时先让测试通过
✗ **不要大规模重构** - 避免一次改动太多代码
✗ **不要盲目重构** - 确保重构有明确目的
✗ **不要过度设计** - 不要为未来可能不会发生的需求重构

## 常见重构模式

### 模式 1：卫语句（Guard Clauses）

```go
// 之前：嵌套条件
func GetPayAmount(employee *Employee) float64 {
    var result float64
    if employee.IsSeparated {
        result = 0
    } else {
        if employee.IsRetired {
            result = 0
        } else {
            result = employee.Salary
        }
    }
    return result
}

// 之后：卫语句
func GetPayAmount(employee *Employee) float64 {
    if employee.IsSeparated {
        return 0
    }
    if employee.IsRetired {
        return 0
    }
    return employee.Salary
}
```

### 模式 2：策略模式替代条件

```go
// 之前：大量 if-else
func CalculatePrice(orderType string, quantity int) float64 {
    if orderType == "regular" {
        return float64(quantity) * 10.0
    } else if orderType == "premium" {
        return float64(quantity) * 15.0
    } else if orderType == "vip" {
        return float64(quantity) * 20.0
    }
    return 0
}

// 之后：策略模式
type PricingStrategy interface {
    Calculate(quantity int) float64
}

type RegularPricing struct{}
func (r RegularPricing) Calculate(quantity int) float64 {
    return float64(quantity) * 10.0
}

type PremiumPricing struct{}
func (p PremiumPricing) Calculate(quantity int) float64 {
    return float64(quantity) * 15.0
}

var strategies = map[string]PricingStrategy{
    "regular": RegularPricing{},
    "premium": PremiumPricing{},
}

func CalculatePrice(orderType string, quantity int) float64 {
    strategy := strategies[orderType]
    return strategy.Calculate(quantity)
}
```

## 输出格式

重构时输出：

```
♻️  重构：[重构内容简述]
   原因：[为什么需要重构]
   技术：[使用的重构技术]

✓ 运行测试
   结果：PASS（X个测试，耗时 Yms）

✓ 重构完成
   改进：[具体改进说明]
```

## 示例输出

```
♻️  重构：提取邮箱验证逻辑
   原因：RegisterUser 和 UpdateUserEmail 中存在重复的验证代码
   技术：Extract Function

   提取前：2 处重复，共 8 行代码
   提取后：1 个函数 validateEmail，被 2 处调用

✓ 运行测试
   命令：go test ./internal/user -v
   结果：PASS
   覆盖率：85.2%

✓ 重构完成
   改进：
   - 消除了 8 行重复代码
   - 提高了可维护性（邮箱验证逻辑集中在一处）
   - 测试覆盖率保持不变
```

## 何时停止重构

满足以下条件即可停止当前重构：

1. ✓ 代码清晰易读，意图明确
2. ✓ 没有明显的代码异味
3. ✓ 函数职责单一，长度适中（< 30 行）
4. ✓ 没有重复代码
5. ✓ 命名准确描述了意图
6. ✓ 所有测试通过

**记住**：重构是持续的过程，不要追求一次性完美。每个 TDD 循环做一点改进即可。

## 参考资料

- 《重构：改善既有代码的设计》- Martin Fowler
- TDD 循环 (tdd-cycle skill)
- 测试优先 (test-first skill)
- SOLID 原则
