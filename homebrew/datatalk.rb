class Datatalk < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
  sha256 "2de7ec8316a0ebce157a792a60a9db15970d680808afe1edbe208e99982a7e7b"
  license "MIT"
  head "https://github.com/vtsaplin/datatalk.git", branch: "main"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"datatalk", "--help"
  end
end
