<!--next-version-placeholder-->

## v0.20.0 (2023-07-25)
### Feature
* **environment:** Added environment variable for setting an S3 bucket prefix ([`97d6f85`](https://github.com/JesseMaitland/superglue/commit/97d6f8541d4413317952b9d4f5eb3502bd55afc1))

## v0.19.1 (2023-03-15)
### Fix
* **tagging:** Fixed a bug where the job override name was not being used in ([`e54fe22`](https://github.com/JesseMaitland/superglue/commit/e54fe2296a1414992877a6238f90127dd49d6082))

## v0.19.0 (2023-03-14)
### Feature
* **tagging:** Add support for adding tags to glue jobs ([`92626b5`](https://github.com/JesseMaitland/superglue/commit/92626b51288ba4359cd740315be359f3694bbe6d))

## v0.18.2 (2023-03-03)
### Fix
* **formatting:** Fix black errors ([`2791217`](https://github.com/JesseMaitland/superglue/commit/2791217ce6c7d0c3776a413981a46333b1defc3a))
* **license:** Add apache 2.0 license and tests for job ([`c8440fb`](https://github.com/JesseMaitland/superglue/commit/c8440fb0efd532b319aa50cea5b6abd3d14b24a3))

## v0.18.1 (2023-02-24)
### Fix
* **job:** Fix a bug that would not deploy additional python files when not using the overrides file ([`3234ef4`](https://github.com/JesseMaitland/superglue/commit/3234ef4323fc55bee2fa54f91cc9e63623227ba2))

## v0.18.0 (2023-01-25)
### Feature
* **superglue:** Bump python version to 3.10 ([`6a59583`](https://github.com/JesseMaitland/superglue/commit/6a595839a2b5e1b559e3ff6181f9b32ea29308a9))

## v0.17.0 (2023-01-17)
### Feature
* **superglue:** Add version option flags to CLI add ignore ([`59c8712`](https://github.com/JesseMaitland/superglue/commit/59c87123e22325d710ad7012a48dffdc25032c77))

## v0.16.0 (2023-01-17)
### Feature
* **superglue:** Add version option flags to CLI fix ([`3befc43`](https://github.com/JesseMaitland/superglue/commit/3befc43df1ca14db189fa302565ee53e29cc4970))

## v0.15.0 (2023-01-17)
### Feature
* **superglue:** Add version option flags to CLI ([`c76a339`](https://github.com/JesseMaitland/superglue/commit/c76a339a4f71f7e311c7526f727d204e01254849))

## v0.14.0 (2023-01-16)
### Feature
* **superglue:** Add refresh command ([`4bb7595`](https://github.com/JesseMaitland/superglue/commit/4bb7595166d38199b7c59e414a5c9d35196497fe))

## v0.13.0 (2023-01-16)
### Feature
* **superglue:** Add refresh command ([`0ff6a8b`](https://github.com/JesseMaitland/superglue/commit/0ff6a8b5e804ec522ca0f249ed0ae4688c339c29))

## v0.12.0 (2023-01-16)
### Feature
* **superglue:** Change config naming convention ([`3261c69`](https://github.com/JesseMaitland/superglue/commit/3261c69bcaeab4dce7e6a3d6ce696ac94c08a481))

## v0.11.0 (2023-01-11)
### Feature
* **overrides:** Fix override bug. copy vs deepcopy ([`62adf8a`](https://github.com/JesseMaitland/superglue/commit/62adf8a4e3b45bfbb0064f7cb432d957bfadfb3f))

## v0.10.0 (2023-01-11)
### Feature
* **ci:** Release for ci changes ([`a367774`](https://github.com/JesseMaitland/superglue/commit/a367774706f962f4e656a7f2fb06a61bb7a8d4ce))
* **formatting:** Fix ([`2c91351`](https://github.com/JesseMaitland/superglue/commit/2c913510a3f61087b0c7e6a90c1222ada8ee7d24))
* **superglue:** Fix rendering ([`e250d9d`](https://github.com/JesseMaitland/superglue/commit/e250d9dd074c325f576672d8293ce59a678f16b4))

## v0.9.0 (2023-01-06)
### Feature
* **package:** Add packaging of all modules ([`af43bd3`](https://github.com/JesseMaitland/superglue/commit/af43bd3629d60a39d79f60a8e36dc096af56ab19))

## v0.8.0 (2023-01-06)
### Feature
* **package:** Add packaging of all modules ([`3106829`](https://github.com/JesseMaitland/superglue/commit/310682944d4f687a56845a2b328d37351a3eb4b6))

## v0.7.0 (2023-01-03)
### Feature
* **ci:** Bump version ([`322efb2`](https://github.com/JesseMaitland/superglue/commit/322efb2827dc692b628879a443c1dbd92e4c4fd3))

## v0.6.0 (2023-01-03)
### Feature
* **ci:** Change fetch depth: ([`65effeb`](https://github.com/JesseMaitland/superglue/commit/65effebc3659e8c71d461755849e690ffdc80c3d))

## v0.5.0 (2022-12-28)
### Feature
* **makefile:** Add glue command ([`2c09ce8`](https://github.com/JesseMaitland/superglue/commit/2c09ce84f167fae18014b7516fdf36af083cdb80))

### Fix
* **formatting:** Fix black errors ([`8901270`](https://github.com/JesseMaitland/superglue/commit/89012703a7b4ec8f60fb3736f4487c353007af94))

## v0.4.0 (2022-12-19)
### Feature
* **cli:** Commands refactored and working ([`adb62c8`](https://github.com/JesseMaitland/superglue/commit/adb62c8f95bdf7d9b014ddfae6da0d5b18905280))

### Fix
* **formatting:** Run black formatter ([`f7708c0`](https://github.com/JesseMaitland/superglue/commit/f7708c0b6ac47efe19b9f1c3b02eda20e59eb9b5))

## v0.3.2 (2022-09-16)
### Fix
* Fixed manifest file ([`07d7481`](https://github.com/JesseMaitland/superglue/commit/07d7481a20b6da6494b6dae009c5c70adc34538c))

## v0.3.1 (2022-09-16)
### Fix
* Added validate environment function ([`3970e9e`](https://github.com/JesseMaitland/superglue/commit/3970e9e20d4f5aeeafbb507a31c9cdd182de3d8d))

## v0.3.0 (2022-09-16)
### Feature
* Enable pypi upload ([`e5d3ed1`](https://github.com/JesseMaitland/superglue/commit/e5d3ed19abb5558b517ba893f17af44eda7c0dd1))

## v0.2.0 (2022-09-16)
### Feature
* Initial release again ([`f4f490d`](https://github.com/JesseMaitland/superglue/commit/f4f490d3fd9a4738ac590e30cd45fe419522793e))

## v0.1.0 (2022-09-16)
### Feature
* Initial release ([`4eb4a06`](https://github.com/JesseMaitland/superglue/commit/4eb4a06f00eef9554719f49d61f59e7ac0a53998))
