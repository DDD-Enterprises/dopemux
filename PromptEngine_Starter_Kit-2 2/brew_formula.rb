class PromptEngine < Formula
  desc "Prompt Wizard CLI Engine"
  homepage "https://yourrepo.com"
  url "https://github.com/youruser/prompt_engine/archive/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_REAL_SHA"
  license "MIT"

  depends_on "python@3.12"

  def install
    system "pip3", "install", "."
    bin.install "bin/prompt-engine"
  end

  test do
    system "#{bin}/prompt-engine", "--help"
  end
end
