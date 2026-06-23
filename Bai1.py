from abc import ABC, abstractmethod

# ==========================================
# 1. GATEWAY CLASSES (Duck Typing Showcase)
# ==========================================

class VNPayGateway:
    """Cổng thanh toán độc lập VNPay."""
    def execute_pay(self, account, amount):
        print(f"[Hệ thống VNPay]: Đang kết nối tới tài khoản {account.account_number}...")
        account.withdraw(amount)
        return True

class ViettelMoneyGateway:
    """Cổng thanh toán độc lập Viettel Money."""
    def execute_pay(self, account, amount):
        print(f"[Hệ thống Viettel Money]: Đang xử lý giao dịch cho tài khoản {account.account_number}...")
        account.withdraw(amount)
        return True


# ==========================================
# 2. CORE BANKING CLASSES (OOP Concepts)
# ==========================================

class BaseAccount(ABC):
    """
    Abstract Base Class định nghĩa bộ khung chuẩn cho mọi loại tài khoản.
    @abstractmethod: Bắt buộc các lớp con phải ghi đè định nghĩa logic cụ thể.
    """
    bank_name = "Vietcombank"

    def __init__(self, account_number, account_holder, initial_balance=0.0):
        if not self.validate_account_number(account_number):
            raise ValueError("Số tài khoản không hợp lệ! Phải gồm đúng 10 chữ số.")
        
        self.account_number = account_number
        self._account_holder = account_holder.strip().upper()
        # Đóng gói nghiêm ngặt qua biến private __balance (Bẫy 1 bảo vệ gián tiếp khi kế thừa)
        self.__balance = float(initial_balance)

    @property
    def account_holder(self):
        """Getter cho tên chủ tài khoản."""
        return self._account_holder

    @account_holder.setter
    def account_holder(self, name):
        """Setter tự động chuẩn hóa tên chủ tài khoản (In hoa, xóa khoảng trắng thừa)."""
        self._account_holder = " ".join(name.strip().split()).upper()

    @property
    def balance(self):
        """@property: Cho phép truy cập đọc số dư một cách an toàn, không có setter trực tiếp."""
        return self.__balance

    # Các phương thức nội bộ để thay đổi số dư an toàn trong nội bộ các lớp con
    def _set_balance(self, amount):
        self.__balance = float(amount)

    @abstractmethod
    def deposit(self, amount):
        """Phương thức trừu tượng nạp tiền."""
        pass

    @abstractmethod
    def withdraw(self, amount):
        """Phương thức trừu tượng rút tiền."""
        pass

    @staticmethod
    def validate_account_number(account_number):
        """@staticmethod: Hàm tiện ích độc lập dùng để kiểm tra tính hợp lệ của số tài khoản."""
        return isinstance(account_number, str) and account_number.isdigit() and len(account_number) == 10

    @classmethod
    def update_bank_name(cls, new_name):
        """@classmethod: Cập nhật tên ngân hàng áp dụng trên toàn bộ các lớp thuộc hệ thống."""
        cls.bank_name = new_name

    # --- Operator Overloading ---
    def __add__(self, other):
        """Nạp chồng toán tử cộng (+). Bẫy số 3: Kiểm tra kiểu dữ liệu kế thừa phù hợp."""
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance + other.balance

    def __lt__(self, other):
        """Nạp chồng toán tử so sánh nhỏ hơn (<). Bẫy số 3: Kiểm tra kiểu dữ liệu kế thừa phù hợp."""
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance < other.balance


class SavingsAccount(BaseAccount):
    """Tài khoản Tiết kiệm với lãi suất năm và phí phạt rút trước hạn."""
    def __init__(self, account_number, account_holder, interest_rate, initial_balance=0.0):
        # Sử dụng super().__init__() để kế thừa thuộc tính khởi tạo từ lớp cha
        super().__init__(account_number, account_holder, initial_balance)
        self.interest_rate = float(interest_rate)

    def deposit(self, amount):
        """Ghi đè phương thức nạp tiền bình thường."""
        if amount <= 0:
            raise ValueError("Số tiền nạp phải lớn hơn 0.")
        self._set_balance(self.balance + amount)

    def withdraw(self, amount):
        """Ghi đè phương thức rút tiền phạt 2% trên số tiền rút trước hạn."""
        if amount <= 0:
            raise ValueError("Số tiền rút phải lớn hơn 0.")
        
        penalty_fee = amount * 0.02
        total_deduction = amount + penalty_fee
        
        if self.balance - total_deduction < 0:
            raise ValueError("Số dư tài khoản không đủ để thực hiện giao dịch và trả phí phạt.")
        
        self._set_balance(self.balance - total_deduction)
        return penalty_fee

    def apply_interest(self):
        """Tính lãi dựa trên số dư hiện tại và cộng thẳng vào tài khoản."""
        interest = self.balance * self.interest_rate
        self._set_balance(self.balance + interest)
        return interest


class CreditAccount(BaseAccount):
    """Tài khoản Tín dụng cho phép chi tiêu thấu chi âm trong hạn mức cho phép."""
    def __init__(self, account_number, account_holder, credit_limit, initial_balance=0.0):
        super().__init__(account_number, account_holder, initial_balance)
        self.credit_limit = float(credit_limit)

    def deposit(self, amount):
        """Ghi đè phương thức nạp tiền để xử lý ghi nợ."""
        if amount <= 0:
            raise ValueError("Số tiền nạp phải lớn hơn 0.")
        self._set_balance(self.balance + amount)

    def withdraw(self, amount):
        """
        Ghi đè phương thức rút tiền hỗ trợ số dư âm.
        Bẫy số 2: Ngăn chặn vượt quá hạn mức tín dụng âm cho phép.
        """
        if amount <= 0:
            raise ValueError("Số tiền rút phải lớn hơn 0.")
        
        if self.balance - amount < -self.credit_limit:
            # Ném lỗi trực tiếp ra hệ thống khi vi phạm hạn mức
            raise ValueError("Vượt quá hạn mức thấu chi cho phép.")
            
        self._set_balance(self.balance - amount)


class DigitalPremiumMixin:
    """Class Mixin độc lập cung cấp ưu đãi số cao cấp, hoàn tiền giao dịch trực tuyến lớn."""
    def cashback_reward(self, amount):
        if amount > 5000000:
            cashback = amount * 0.01
            return cashback
        return 0.0


class HybridAccount(SavingsAccount, DigitalPremiumMixin):
    """Tài khoản tích hợp Đa năng thụ hưởng đa kế thừa & tuân thủ chuẩn MRO."""
    def __init__(self, account_number, account_holder, interest_rate, initial_balance=0.0):
        super().__init__(account_number, account_holder, interest_rate, initial_balance)


# ==========================================
# 3. GLOBAL SYSTEM FUNCTIONS (Duck Typing Engine)
# ==========================================

def process_payment(payment_gateway, account, amount):
    """
    Hàm toàn cục ứng dụng Duck Typing linh hoạt.
    Bẫy số 4: Bắt lỗi AttributeError nếu đối tượng truyền vào không có hàm thực thi thanh toán.
    """
    try:
        if not hasattr(payment_gateway, 'execute_pay'):
            raise AttributeError("Cổng thanh toán không hợp lệ hoặc chưa được tích hợp.")
        
        return payment_gateway.execute_pay(account, amount)
    except AttributeError as e:
        print(f"Lỗi: {e}")
        return False
    except Exception as e:
        print(f"Giao dịch thất bại: {e}")
        return False


# ==========================================
# 4. CLI MENU SYSTEM
# ==========================================

def main():
    accounts = []
    current_account = None

    # Tạo sẵn một tài khoản đối ứng phụ phục vụ việc test tính năng Overloading ở menu 5
    backup_acc = SavingsAccount("0987654321", "TRAN THI BINH", 0.05, 15000000)
    accounts.append(backup_acc)

    while True:
        print("\n===== VIETCOMBANK DIGIBANK PRO SIMULATOR =====")
        print("1. Mở tài khoản mới (Chọn loại tài khoản)")
        print("2. Xem thông tin & Kiểm tra thứ tự kế thừa (MRO)")
        print("3. Giao dịch Nạp / Rút tiền & Tính điểm thưởng (Đa hình)")
        print("4. Tích lũy / Áp dụng lãi suất định kỳ")
        print("5. Kiểm tra tính năng gộp tài khoản & So sánh (Overloading)")
        print("6. Thanh toán hóa đơn qua Cổng trung gian (Duck Typing)")
        print("7. Thoát chương trình")
        print("==============================================")
        
        choice = input("Chọn chức năng (1-7): ").strip()

        if choice == "1":
            print("\n--- CHỌN LOẠI TÀI KHOẢN ---")
            print("1. Savings Account (Tài khoản Tiết kiệm)")
            print("2. Credit Account (Tài khoản Tín dụng)")
            print("3. Hybrid Account (Tài khoản Đa năng)")
            type_choice = input("Chọn loại tài khoản (1-3): ").strip()
            
            acc_num = input("Nhập số tài khoản 10 chữ số: ").strip()
            # Bẫy dữ liệu ngay khi nhập số tài khoản bằng Static Method
            if not BaseAccount.validate_account_number(acc_num):
                print("Số tài khoản không hợp lệ! Phải gồm đúng 10 chữ số.")
                continue

            name = input("Nhập tên chủ tài khoản: ")
            
            try:
                if type_choice == "1":
                    rate = float(input("Nhập lãi suất năm (ví dụ 0.05): "))
                    current_account = SavingsAccount(acc_num, name, rate, 10000000.0) # Khởi tạo mẫu 10 triệu
                    print(f"\nMở tài khoản Tiết kiệm thành công!\nChủ tài khoản: {current_account.account_holder}")
                elif type_choice == "2":
                    limit = float(input("Nhập hạn mức tín dụng (ví dụ 20000000): "))
                    current_account = CreditAccount(acc_num, name, limit, 0.0) # Tín dụng mặc định balance = 0
                    print(f"\nMở tài khoản Tín dụng thành công!\nChủ tài khoản: {current_account.account_holder}")
                elif type_choice == "3":
                    rate = float(input("Nhập lãi suất năm (ví dụ 0.06): "))
                    current_account = HybridAccount(acc_num, name, rate, 10000000.0) # Khởi tạo mẫu 10 triệu
                    print(f"\nMở tài khoản Đa năng thành công!\nChủ tài khoản: {current_account.account_holder}")
                else:
                    print("Lựa chọn không hợp lệ.")
                    continue
                
                accounts.append(current_account)
            except Exception as e:
                print(f"Lỗi khởi tạo tài khoản: {e}")

        elif choice == "2":
            if not current_account:
                print("Hệ thống chưa có thông tin tài khoản. Vui lòng mở tài khoản ở Chức năng 1 trước.")
                continue
            
            print("\n--- THÔNG TIN TÀI KHOẢN HIỆN TẠI ---")
            print(f"Loại tài khoản: {type(current_account).__name__}")
            print(f"Ngân hàng: {current_account.bank_name}")
            print(f"Số tài khoản: {current_account.account_number}")
            print(f"Chủ tài khoản: {current_account.account_holder}")
            print(f"Số dư: {current_account.balance:,.0f} VND")
            
            if hasattr(current_account, 'interest_rate'):
                print(f"Lãi suất: {current_account.interest_rate * 100}% / năm")
            if hasattr(current_account, 'credit_limit'):
                print(f"Hạn mức tín dụng: {current_account.credit_limit:,.0f} VND")
            
            print("\n--- KIỂM TRA MRO (Danh sách kế thừa công khai) ---")
            for idx, cls in enumerate(type(current_account).__mro__):
                print(f" [{idx}]: {cls}")

        elif choice == "3":
            if not current_account:
                print("Hệ thống chưa có thông tin tài khoản.")
                continue
            
            print("\n--- GIAO DỊCH NẠP / RÚT TIỀN ---")
            print("1. Nạp tiền")
            print("2. Rút tiền")
            tx_choice = input("Chọn giao dịch (1-2): ").strip()
            
            try:
                amount = float(input("Nhập số tiền giao dịch: "))
                if tx_choice == "1":
                    # Đa hình trong việc kích hoạt phần thưởng nếu thuộc dòng tài khoản Hybrid
                    current_account.deposit(amount)
                    print(f"Nạp tiền thành công!")
                    if isinstance(current_account, HybridAccount):
                        bonus = current_account.cashback_reward(amount)
                        if bonus > 0:
                            current_account.deposit(bonus)
                            print(f"[Ưu đãi Premium]: Bạn được hoàn tiền 1% ({bonus:,.0f} VND) vào tài khoản!")
                    print(f"Số dư mới: {current_account.balance:,.0f} VND")
                    
                elif tx_choice == "2":
                    # Tính Đa hình (Polymorphism) tự thay đổi hành vi rút tiền
                    penalty = current_account.withdraw(amount)
                    print(f"Rút tiền thành công! {('(Sử dụng hạn mức thấu chi)' if current_account.balance < 0 else '')}")
                    print(f"Số tiền rút: {amount:,.0f} VND")
                    if penalty:
                        print(f"Phí phạt rút trước hạn (2%): {penalty:,.0f} VND")
                    print(f"Số dư còn lại: {current_account.balance:,.0f} VND")
            except Exception as e:
                # Xử lý mượt mà Edge Case 2 (Vượt hạn mức tín dụng âm hoặc không đủ số dư)
                print(f"Giao dịch thất bại! Lỗi: {e}")

        elif choice == "4":
            if not current_account:
                print("Hệ thống chưa có thông tin tài khoản.")
                continue
            
            if hasattr(current_account, 'apply_interest'):
                print("\n--- TÍNH LÃI ĐỊNH KỲ ---")
                print(f"Số dư trước tính lãi: {current_account.balance:,.0f} VND")
                interest_earned = current_account.apply_interest()
                print(f"Lãi suất năm: {current_account.interest_rate * 100}%")
                print(f"Tiền lãi nhận được: +{interest_earned:,.0f} VND")
                print(f"Số dư mới sau khi cộng lãi: {current_account.balance:,.0f} VND")
            else:
                print("Tính năng không hỗ trợ! Tài khoản này không có tính chất sinh lãi tiết kiệm.")

        elif choice == "5":
            if not current_account:
                print("Hệ thống chưa có thông tin tài khoản.")
                continue
            
            print("\n--- ĐỒNG BỘ & SO SÁNH TÀI KHOẢN (OPERATOR OVERLOADING) ---")
            print(f"Tài khoản hiện tại (A): {current_account.account_holder} (Số dư: {current_account.balance:,.0f} VND)")
            print(f"Tài khoản đối ứng (B) sẵn có: {backup_acc.account_holder} (Số dư: {backup_acc.balance:,.0f} VND)")
            
            # Thực thi so sánh (__lt__)
            if current_account < backup_acc:
                print("[Kết quả So sánh (__lt__)]: Số dư tài khoản A NHỎ HƠN số dư tài khoản B.")
            else:
                print("[Kết quả So sánh (__lt__)]: Số dư tài khoản A LỚN HƠN HOẶC BẰNG số dư tài khoản B.")
            
            # Thực thi cộng gộp (__add__)
            total_sum = current_account + backup_acc
            print(f"[Kết quả Tổng hợp (__add__)]: Tổng số tiền sở hữu của cả 2 tài khoản là: {total_sum:,.0f} VND.")
            
            # Thử nghiệm Bẫy dữ liệu số 3 (Cộng với kiểu dữ liệu không hợp lệ như int)
            print("\n[Thử nghiệm Edge Case 3]: Cộng tài khoản A với một số nguyên (1,000,000)...")
            try:
                result = current_account + 1000000
                if result == NotImplemented:
                    raise TypeError("Không thể cộng đối tượng tài khoản với kiểu dữ liệu không phải tài khoản.")
            except TypeError:
                print(">> Bẫy thành công: Hệ thống từ chối tính toán và trả về ngoại lệ chuẩn xác!")

        elif choice == "6":
            if not current_account:
                print("Hệ thống chưa có thông tin tài khoản.")
                continue
            
            print("\n--- THANH TOÁN HÓA ĐƠN QUA CỔNG TRUNG GIAN ---")
            print("1. Thanh toán qua VNPay")
            print("2. Thanh toán qua Viettel Money")
            print("3. Thử nghiệm Cổng lỗi (Không tích hợp hàm execute_pay)")
            gt_choice = input("Chọn cổng thanh toán (1-3): ").strip()
            
            try:
                bill_amount = float(input("Nhập số tiền hóa đơn: "))
                
                if gt_choice == "1":
                    gateway = VNPayGateway()
                elif gt_choice == "2":
                    gateway = ViettelMoneyGateway()
                elif gt_choice == "3":
                    # Lớp giả lập bị lỗi để test bẫy 4
                    class FakeGateway: pass
                    gateway = FakeGateway()
                else:
                    print("Lựa chọn không hợp lệ.")
                    continue
                
                # Gọi hàm xử lý Duck Typing
                success = process_payment(gateway, current_account, bill_amount)
                if success:
                    print("Xác thực thanh toán bằng Duck Typing thành công!")
                    print(f"Tài khoản đã thanh toán hóa đơn giá trị: {bill_amount:,.0f} VND.")
                    print(f"Số dư mới: {current_account.balance:,.0f} VND.")
            except Exception as e:
                print(f"Lỗi hệ thống: {e}")

        elif choice == "7":
            print("\nCảm ơn đã trải nghiệm hệ thống Vietcombank Digibank Pro Simulator!")
            break
        else:
            print("Vui lòng chọn lại các tính năng hiển thị từ 1 đến 7.")

if __name__ == "__main__":
    # Minh họa trực quan Edge Case 1 (Khởi tạo trực tiếp Abstract Base Class)
    print("[Kiểm tra hệ thống độc lập] Đang thử khởi tạo trực tiếp lớp trừu tượng BaseAccount...")
    try:
        acc = BaseAccount("1234567890", "Test ABC")
    except TypeError as e:
        print(f">> Bẫy thành công 1: Hệ thống ngăn chặn thành công! Lỗi nhận diện: {e}\n")
    
    # Kích hoạt hệ thống Core
    main()