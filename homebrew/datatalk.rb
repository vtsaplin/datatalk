cla  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "c0aa7399ce942e9b2dda12ebd1e4de1557cd039e705e3a39784d48f23cc1fea6"
  license "MIT"tatalk < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/tsaplin/datatalk"
  url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "c0aa7399ce942e9b2dda12ebd1e4de1557cd039e705e3a39784d48f23cc1fea6"
  license "MIT"
  head "https://github.com/vtsaplin/datatalk.git", branch: "main"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/datatalk", "--help"
  end
end
