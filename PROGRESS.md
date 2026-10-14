# Tiến độ Lab 11 — đã hoàn thành CP0–CP9

Cập nhật ngày 14/10/2026. MSSV **202602818**, thị trấn **A**.

## Trạng thái hoàn thành

- CP0–CP4: môi trường, replay, bộ lọc khả thi, Monte Carlo và bốn cuộc săn CEM đã xong.
- CP5: hoàn thành log_weights, is_estimate; chạy đủ 3 seed IS. Trung vị total ≈ 0.000542358782, chênh giữa seed khoảng 4 lần. Có cảnh báo suy biến trọng số trong REPORT.
- CP6: hoàn thành progress_metrics, choose_policy. Chọn từ TRAIN: {"cutinLat": 3.0}. TEST: fail gốc ≈ 0.001030041596; bản chọn ≈ 0.0000005976101974. fail_hi của bản chọn ≈ 0.038779871468 do chưa có hit bus_bypass, không được diễn giải rằng đã chứng nhận an toàn. TEST giảm quãng đường khoảng 0,088879%.
- CP7: xuất viewer.json sau fix/mine; chụp và kiểm tra bốn ảnh thực tế trong evidence/shots/. File fix_comparison_viewer.json bổ sung dùng xe đặc là bản chọn, bóng mờ là policy gốc.
- CP8: dựng hazard.json từ chương 10, người đi bộ chậm băng ngang ngoài vạch trên đường ướt. world=scene đã được người dùng chọn. Quét 1500 biến thể, accepted=100%. Cả policy gốc và bản chọn có 371 avoidable, 0 unavoidable, 0 unattributed; low_speed=5. Wilson [0.22616213796883855, 0.26979541500748555]. Bản sửa lấn làn chưa giải quyết cơ chế này.
- CP9: REPORT.md đã trả lời đủ 9 câu, trích số từ JSON, có ảnh và nguồn tham khảo. Đã kiểm tra nhất quán artifact và chạy lại chính xác cảnh hazard.

## Kiểm tra

- 31/31 test TODO đạt trong WSL.
- 10/10 test parity Python–JavaScript đạt qua Python và Node trên Windows.
- Không sửa avsim/, run_all.py, tests/, policy_candidates.json, requirements.txt, phân phối tự nhiên hoặc seed.
- Đã chạy đủ từng bước world, replay, mc, hunt, estimate, fix, mine, export ở ngân sách đầy đủ. Các bước chạy riêng, không cần chạy lại chỉ để tạo một invocation all. Evidence không dùng --quick.
- evidence/validation.json ghi kết quả kiểm tra. Bộ chấm ẩn/seed TEST bí mật của giảng viên chưa có để chạy.

## Mở bài và xem kết quả

Trong WSL tại thư mục lab:

```bash
source .venv/bin/activate
python -m pytest -q tests/test_todos.py
python tools/verify_submission.py
```

Mở viewer/index.html bằng trình duyệt:

- Chương 9: nạp evidence/viewer.json, chọn B-01 tại 12.75 s hoặc C-01 tại 18.75 s.
- Để xem xe đặc là bản sửa và bóng mờ là bản gốc: nạp evidence/fix_comparison_viewer.json, chọn F-01 tại 12.75 s.
- Chương 10: mở hazard.json, xem tiếp xúc người đi bộ tại 18.25 s.

Muốn chạy lại toàn bộ từ code hiện tại:

```bash
python run_all.py all
python tools/capture_evidence.py
python tools/complete_report.py
python tools/verify_submission.py
```

Lưu ý capture_evidence.py được chạy thành công bằng Windows Python có playwright và Chromium. Đây là phụ thuộc bổ sung chỉ để chụp ảnh, không phải phụ thuộc pipeline lab. Lần chạy lại all có thể mất nhiều phút. Bộ verifier không tự chạy lại các bộ test; số test trong validation là kết quả đã quan sát trong lần hoàn thiện này.

## Giới hạn và phần người dùng cần đọc lại

- hazard dùng kết quả có điều kiện trên một cảnh, không phải tần suất giao thông thật. exposure=1 chỉ mô tả một rắc rối chèn mỗi lượt thử; không nhân để so với xác suất toàn thị trấn. Căn cứ và nguồn nằm trong hazard.json: why và REPORT câu 9.
- Chưa có thử nghiệm tự lái của người dùng; REPORT ghi rõ, không bịa kết quả.
- Không kết luận xác suất thật bằng 0 khi không có hit. Không chọn lại policy dựa trên TEST công khai.
- safer_knob_case.json, visual_checks.json, fix_comparison_viewer.json và validation.json là bằng chứng/kiểm tra bổ sung; không phải các output chính do run_all.py sinh.

## Nộp bài và sao lưu

Nộp lab11/*.py, hazard.json, evidence/*.json, evidence/shots/ và REPORT.md theo README. Có thể kèm tools/ và PROGRESS.md để tái tạo báo cáo/ảnh. Code và evidence được chia thành commit theo CP để nộp qua Git; trạng thái push được xác nhận trong chat. evidence/ vẫn nằm trong .gitignore nhưng các JSON và ảnh nộp bài đã được thêm cưỡng bức để Git theo dõi. Khi tạo thêm evidence mới, kiểm tra git status và thêm file cần nộp.

Bản ZIP hoàn thiện ở thư mục cha có hậu tố COMPLETED-20261014.zip (nếu tên đã tồn tại sẽ thêm số). ZIP bao gồm evidence, ảnh, code và báo cáo; bỏ môi trường .venv, .git và cache. Trên máy mới tạo .venv và cài requirements.txt để chạy pipeline.
