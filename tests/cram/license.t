simon license operates only on git-tracked files

  $ mkdir -p git-test && cd git-test

  $ git init
  Initialized empty Git repository in (.*) (re)

  $ echo "int main() {}" > main.cpp
  $ git add main.cpp
  $ git config user.email "foo@bar.com"
  $ git config user.name "foobar"
  $ git commit -m "Initial commit" > /dev/null

  $ simon license check
  [ERROR] File does not contain valid license text: main.cpp
  [1]

  $ simon license apply
  [INFO] Prepending license text to file: main.cpp

  $ simon license check

  $ cat main.cpp
  /**
  * Copyright 2017 BitTorrent Inc.
  *
  * Licensed under the Apache License, Version 2.0 (the "License");
  * you may not use this file except in compliance with the License.
  * You may obtain a copy of the License at
  *
  *    http://www.apache.org/licenses/LICENSE-2.0
  *
  * Unless required by applicable law or agreed to in writing, software
  * distributed under the License is distributed on an "AS IS" BASIS,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  */
  int main() {}
