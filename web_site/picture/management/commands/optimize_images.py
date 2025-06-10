import os
from io import BytesIO

from django.core.files import File
from django.core.management.base import BaseCommand
from PIL import Image

from picture.models import Picture


class Command(BaseCommand):
    help = "既存の画像を最適化します"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="実際に変更を加えずに処理をシミュレートします",
        )
        parser.add_argument(
            "--max-size",
            type=int,
            nargs=2,
            default=[1920, 1080],
            help="最大画像サイズ（幅 高さ）",
        )
        parser.add_argument(
            "--quality",
            type=int,
            default=85,
            help="圧縮品質（0-100）",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["webp", "avif", "jpeg"],
            default="webp",
            help="出力形式（webp, avif, jpeg）",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        max_size = tuple(options["max_size"])
        quality = options["quality"]
        output_format = options["format"]

        pictures = Picture.objects.all()
        total = pictures.count()
        processed = 0
        optimized = 0
        skipped = 0
        errors = 0

        self.stdout.write(
            f"合計 {total} 個の画像を処理します..."
        )

        for picture in pictures:
            try:
                if not picture.file:
                    self.stdout.write(
                        f"スキップ: ID {picture.id} - ファイルが存在しません"
                    )
                    skipped += 1
                    continue

                # 元のファイルサイズを取得
                original_size = os.path.getsize(
                    picture.file.path
                )

                # 画像を開く
                im = Image.open(picture.file.path)

                # 画像が既に最適化されているかチェック
                if (
                    im.format.upper()
                    == output_format.upper()
                    and im.width <= max_size[0]
                    and im.height <= max_size[1]
                ):
                    self.stdout.write(
                        f"スキップ: ID {picture.id} - 既に最適化されています"
                    )
                    skipped += 1
                    continue

                # 透過を保持するかどうかを判断
                has_alpha = im.mode in ("RGBA", "LA") or (
                    im.mode == "P"
                    and "transparency" in im.info
                )

                # 画像モードの変換
                if output_format == "avif" and has_alpha:
                    # AVIFは透過をサポート
                    if im.mode != "RGBA":
                        im = im.convert("RGBA")
                elif output_format == "webp" and has_alpha:
                    # WebPは透過をサポート
                    if im.mode != "RGBA":
                        im = im.convert("RGBA")
                else:
                    # JPEGは透過をサポートしない
                    if im.mode != "RGB":
                        im = im.convert("RGB")

                # リサイズ
                if (
                    im.width > max_size[0]
                    or im.height > max_size[1]
                ):
                    im.thumbnail(
                        max_size, Image.Resampling.LANCZOS
                    )

                # 画像をメモリ上で圧縮
                output = BytesIO()

                # 形式に応じた保存オプション
                save_options = {
                    "quality": quality,
                    "optimize": True,
                }

                if output_format == "webp":
                    save_options["method"] = 6  # 最高圧縮率
                elif output_format == "avif":
                    save_options["speed"] = 8  # 最高圧縮率

                im.save(
                    output,
                    format=output_format.upper(),
                    **save_options,
                )
                output.seek(0)

                if not dry_run:
                    # 元のファイル名を維持（拡張子のみ変更）
                    filename = os.path.basename(
                        picture.file.name
                    )
                    name, _ = os.path.splitext(filename)
                    new_filename = f"{name}.{output_format}"

                    # ファイルを保存
                    picture.file.save(
                        new_filename,
                        File(output),
                        save=True,
                    )

                    # 新しいファイルサイズを取得
                    new_size = os.path.getsize(
                        picture.file.path
                    )
                    size_reduction = (
                        (original_size - new_size)
                        / original_size
                    ) * 100

                    self.stdout.write(
                        f"最適化完了: ID {picture.id} - "
                        f"サイズ削減: {size_reduction:.1f}% "
                        f"({original_size / 1024:.1f}KB → {new_size / 1024:.1f}KB)"
                    )
                else:
                    self.stdout.write(
                        f"シミュレーション: ID {picture.id} を最適化します"
                    )

                optimized += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"エラー: ID {picture.id} - {str(e)}"
                    )
                )
                errors += 1

            processed += 1
            if processed % 10 == 0:
                self.stdout.write(
                    f"進捗: {processed}/{total} 画像を処理しました"
                )

        # 結果の表示
        self.stdout.write("\n処理完了:")
        self.stdout.write(f"- 処理済み: {processed}")
        self.stdout.write(f"- 最適化: {optimized}")
        self.stdout.write(f"- スキップ: {skipped}")
        self.stdout.write(f"- エラー: {errors}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nこれはドライランです。実際の変更は加えられていません。"
                )
            )
