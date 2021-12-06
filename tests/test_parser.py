# coding: utf-8

import os
from unittest import TestCase

from nist_tests_vectors import RspFile, RspParsingError, TestVector, TestVectors

THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestTestVectors(TestCase):

    def test_value_parsing(self):
        self.assertEqual(TestVector.parse_vector_value("0"), 0)
        self.assertEqual(TestVector.parse_vector_value("42"), 42)
        self.assertEqual(TestVector.parse_vector_value(str(2**32 - 1)), 2**32 - 1)

        self.assertEqual(TestVector.parse_vector_value("00"), bytearray(b"\x00"))
        self.assertEqual(TestVector.parse_vector_value("aa"), bytearray(b"\xaa"))
        self.assertEqual(TestVector.parse_vector_value("00000042"), bytearray(b"\x00\x00\x00\x42"))
        self.assertEqual(TestVector.parse_vector_value(str(2**32)), bytearray(b"\x42\x94\x96\x72\x96"))

        with self.assertRaises(ValueError):
            TestVector.parse_vector_value("something random")

    def test_vectors_iterable(self):
        test_vectors = TestVectors()
        test_vectors.append(TestVector("COUNT", 1))
        self.assertEqual(len(test_vectors), 1)
        # TODO


class TestRspParsing(TestCase):

    def test_rspfile(self):
        with RspFile(f"{THIS_SCRIPT_DIR}/data/XTSGenAES128.rsp") as rsp_file:
            # Make sure RspFile's __iter__ is reentrant and that 
            # ProfileIterator's __next__ works properly
            self.assertEqual(len(rsp_file.profiles), 2)
            self.assertEqual(len(rsp_file.profiles), 2)

            for profile in rsp_file:
                # Make sure Profile's __iter__ is reentrant and that 
                # TestVectorsIterator's __next__ works properly
                self.assertEqual(len([v for v in profile.vectors]), 500)
                self.assertEqual(len([v for v in profile.vectors]), 500)


    def test_weird_rspfile(self):
        with RspFile(f"{THIS_SCRIPT_DIR}/data/unusual_format_but_still_valid.rsp") as rsp_file:
            for profile in rsp_file:
                for test_vector in profile.vectors:
                    self.assertEqual(len(test_vector), 8)

            # This file contains an empty profile with no test vector
            self.assertEqual(len(list(rsp_file.profiles[-1].vectors)), 0)


    # This is an anoying feature to support, let's wait to see if there's any file like this
    # def test_no_profile(self):
    #     with RspFile(f"{THIS_SCRIPT_DIR}/data/no_profile.rsp") as rsp_file:
    #         self.assertEqual(len(rsp_file.profiles), 1)


    def test_malformed_rspfile(self):
        with RspFile(f"{THIS_SCRIPT_DIR}/data/malformed1.rsp") as rsp_file:
            with self.assertRaisesRegex(RspParsingError, "fields inconsistency"):
                for profile in rsp_file:
                    list(profile.vectors)

        with RspFile(f"{THIS_SCRIPT_DIR}/data/malformed3.rsp") as rsp_file:
            with self.assertRaisesRegex(RspParsingError, "Duplicated attribute"):
                rsp_file.profiles

        with RspFile(f"{THIS_SCRIPT_DIR}/data/malformed6.rsp") as rsp_file:
            with self.assertRaisesRegex(RspParsingError, "Duplicated key: Key"):
                for profile in rsp_file:
                    list(profile.vectors)

        with RspFile(f"{THIS_SCRIPT_DIR}/data/malformed7.rsp") as rsp_file:
            with self.assertRaisesRegex(RspParsingError, "Expected integer or hex"):
                for profile in rsp_file:
                    list(profile.vectors)

        with RspFile(f"{THIS_SCRIPT_DIR}/data/malformed8.rsp") as rsp_file:
            with self.assertRaisesRegex(RspParsingError, "Invalid profile attribute"):
                for profile in rsp_file:
                    list(profile.vectors)

    def test_XTSGenAES128(self):
        with RspFile(f"{THIS_SCRIPT_DIR}/data/XTSGenAES128.rsp") as rsp_file:
            profiles = rsp_file.profiles
            self.assertEqual(len(profiles), 2)

            encrypt_profile = profiles[0]
            decrypt_profile = profiles[1]

            self.assertEqual(encrypt_profile.attributes, {"ENCRYPT": ""})
            self.assertEqual(decrypt_profile.attributes, {"DECRYPT": ""})

            encrypt_tests = list(encrypt_profile.vectors)
            decrypt_tests = list(decrypt_profile.vectors)

            self.assertEqual(len(encrypt_tests), 500)
            self.assertEqual(len(decrypt_tests), 500)

            # First and last vector of the [ENCRYPT] profile
            self.assertEqual(encrypt_tests[0]["COUNT"], 1)
            self.assertEqual(encrypt_tests[0]["DataUnitLen"], 128)
            self.assertEqual(encrypt_tests[0]["Key"], bytearray.fromhex("a1b90cba3f06ac353b2c343876081762090923026e91771815f29dab01932f2f"))
            self.assertEqual(encrypt_tests[0]["i"], bytearray.fromhex("4faef7117cda59c66e4b92013e768ad5"))
            self.assertEqual(encrypt_tests[0]["PT"], bytearray.fromhex("ebabce95b14d3c8d6fb350390790311c"))
            self.assertEqual(encrypt_tests[0]["CT"], bytearray.fromhex("778ae8b43cb98d5a825081d5be471c63"))

            self.assertEqual(encrypt_tests[-1]["COUNT"], 500)
            self.assertEqual(encrypt_tests[-1]["DataUnitLen"], 256)
            self.assertEqual(encrypt_tests[-1]["Key"], bytearray.fromhex("783a83ec52a27405dff9de4c57f9c979b360b6a5df88d67ec1a052e6f582a717"))
            self.assertEqual(encrypt_tests[-1]["i"], bytearray.fromhex("886e975b29bdf6f0c01bb47f61f6f0f5"))
            self.assertEqual(encrypt_tests[-1]["PT"], bytearray.fromhex("b04d84da856b9a59ce2d626746f689a8051dacd6bce3b990aa901e4030648879"))
            self.assertEqual(encrypt_tests[-1]["CT"], bytearray.fromhex("f941039ebab8cac39d59247cbbcb4d816c726daed11577692c55e4ac6d3e6820"))


            # First and last vector of the [DECRYPT] profile
            self.assertEqual(decrypt_tests[0]["COUNT"], 1)
            self.assertEqual(decrypt_tests[0]["DataUnitLen"], 128)
            self.assertEqual(decrypt_tests[0]["Key"], bytearray.fromhex("c43cd0b23798ee3db0053d1e4d185e965d67fdda8c5325cc709fc3973f05cd17"))
            self.assertEqual(decrypt_tests[0]["i"], bytearray.fromhex("7900432e6021bc0e627c7b96ca08b4d0"))
            self.assertEqual(decrypt_tests[0]["CT"], bytearray.fromhex("3454f7d34c0caffa12e9d2850b037fff"))
            self.assertEqual(decrypt_tests[0]["PT"], bytearray.fromhex("07f2c2d4e6db6e1200bc165d154e0698"))

            self.assertEqual(decrypt_tests[-1]["COUNT"], 500)
            self.assertEqual(decrypt_tests[-1]["DataUnitLen"], 256)
            self.assertEqual(decrypt_tests[-1]["Key"], bytearray.fromhex("bf14b298e9c72ca73676915a80fa2fac4fe2b56ebc4df57e3028fd4a41ac9e1c"))
            self.assertEqual(decrypt_tests[-1]["i"], bytearray.fromhex("5e49263efac5451ee395083c25de2c13"))
            self.assertEqual(decrypt_tests[-1]["CT"], bytearray.fromhex("63a98f178be85688a8a5ce00b25bf08a972d34ece95c6947260e6e44fdbaa357"))
            self.assertEqual(decrypt_tests[-1]["PT"], bytearray.fromhex("401efe5c41cea23da0d33caa946b916c88ad99d65fb8238047597b94bcdb88b7"))

            # Make sure test vectors all have the same amount of attributes
            for test_vector in encrypt_tests:
                self.assertEqual(len(test_vector), 6)

    def test_KDFFeedback_gen(self):
        with RspFile(f"{THIS_SCRIPT_DIR}/data/KDFFeedback_gen.rsp") as rsp_file:
            profiles = rsp_file.profiles
            self.assertEqual(len(profiles), 120)

            cmac_aes128_profile = profiles[0]
            cmac_tdes2_profile = profiles[36]
            hmac_sha1_profile = profiles[60]
            hmac_sha512_profile = profiles[119]

            self.assertEqual(cmac_aes128_profile.attributes, {"PRF": "CMAC_AES128", "CTRLOCATION": "BEFORE_ITER", "RLEN": "8_BITS"})
            self.assertEqual(cmac_tdes2_profile.attributes, {"PRF": "CMAC_TDES2", "CTRLOCATION": "BEFORE_ITER", "RLEN": "8_BITS"})
            self.assertEqual(hmac_sha1_profile.attributes, {"PRF": "HMAC_SHA1", "CTRLOCATION": "BEFORE_ITER", "RLEN": "8_BITS"})
            self.assertEqual(hmac_sha512_profile.attributes, {"PRF": "HMAC_SHA512", "CTRLOCATION": "AFTER_FIXED", "RLEN": "32_BITS"})

            cmac_aes128_tests = list(profiles[0].vectors)
            cmac_tdes2_tests = list(profiles[36].vectors)
            hmac_sha1_tests = list(profiles[60].vectors)
            hmac_sha512_tests = list(profiles[119].vectors)

            self.assertEqual(len(cmac_aes128_tests), 40)
            self.assertEqual(len(cmac_tdes2_tests), 40)
            self.assertEqual(len(hmac_sha1_tests), 40)
            self.assertEqual(len(hmac_sha512_tests), 40)

            # First and last vector of the [PRF=CMAC_AES128] profile
            self.assertEqual(cmac_aes128_tests[0]["COUNT"], 0)
            self.assertEqual(cmac_aes128_tests[0]["L"], 512)
            self.assertEqual(cmac_aes128_tests[0]["KI"], bytearray.fromhex("6874c099a14942d5bcd823183a4ceb9c"))
            self.assertEqual(cmac_aes128_tests[0]["IVlen"], 128)
            self.assertEqual(cmac_aes128_tests[0]["IV"], bytearray.fromhex("4ab31c84730527fbf008e446501bb26a"))
            self.assertEqual(cmac_aes128_tests[0]["FixedInputDataByteLen"], 51)
            self.assertEqual(cmac_aes128_tests[0]["FixedInputData"], bytearray.fromhex("0909d62821ec989fe16d6d77358126d272fff3e2dc4795c5a9421bee65be679b9f651668fdbc2c13d2ef4932f8830b56e5e1e0"))
            self.assertEqual(cmac_aes128_tests[0]["KO"], bytearray.fromhex("265062a5de896edbfc0d071bdfb6dfd18901f3786cee3c401e53c198e80e78bab17c7049c723d4cd9d334952509c44d7e7bc16627a1e7177b80157a3c56ac21b"))

            self.assertEqual(cmac_aes128_tests[-1]["COUNT"], 39)
            self.assertEqual(cmac_aes128_tests[-1]["L"], 2400)
            self.assertEqual(cmac_aes128_tests[-1]["KI"], bytearray.fromhex("b214db625037492f66bb70c42ea6a4e9"))
            self.assertEqual(cmac_aes128_tests[-1]["IVlen"], 128)
            self.assertEqual(cmac_aes128_tests[-1]["IV"], bytearray.fromhex("56d627458c844cef01e17e03a47cd804"))
            self.assertEqual(cmac_aes128_tests[-1]["FixedInputDataByteLen"], 51)
            self.assertEqual(cmac_aes128_tests[-1]["FixedInputData"], bytearray.fromhex("0f44d16d9dbf68d74732500ab578b4ec6b08bea17bed4af0ba8f7fa52f45391ac2d23096ceb1fe5d3915d4e300f6434aa616d4"))
            self.assertEqual(cmac_aes128_tests[-1]["KO"], bytearray.fromhex("c2339ef81b084bf12c347f47037512838cc8e14b028427485ce393ad73f0d934b399bd5c21b5d39f4f5a0c43e3c0603d87c8e0c49e530309f09d126836fc61cfd7d7c5fa4200071c600a9dbc99832e7b1a4bff6236fdbf7c2bb312cf612aae63d9fdc090ddb756c2dd89ab721307d3a4403a53da2b7befad86cc8662104eae995bdd19fb0dee5001721e42b14390da822a6d877572909385ef9b9802f33fb527594a3edd765b17d73e56185e9342e15587598ee1e08b8764691b8a31f79860e4d05d3d7a968669251dd1ed924cdcc360d0fe65bd1c3967b34193c7494d929a1554a11399a04d7466c52d01acafc7a6a21940c997b208c2dcba8e82e1b2b525410a455440abfa6394a2b7a9fad415541dc3487f44ab936723761c8425796f06478b098a0f492e40eb495028e4"))

            # First and last vector of the [PRF=CMAC_TDES2] profile
            self.assertEqual(cmac_tdes2_tests[0]["COUNT"], 0)
            self.assertEqual(cmac_tdes2_tests[0]["L"], 512)
            self.assertEqual(cmac_tdes2_tests[0]["KI"], bytearray.fromhex("8c6c3838d02fc8df7f398f44efa065e9"))
            self.assertEqual(cmac_tdes2_tests[0]["IVlen"], 64)
            self.assertEqual(cmac_tdes2_tests[0]["IV"], bytearray.fromhex("a5dca1e9447d865a"))
            self.assertEqual(cmac_tdes2_tests[0]["FixedInputDataByteLen"], 51)
            self.assertEqual(cmac_tdes2_tests[0]["FixedInputData"], bytearray.fromhex("f3f683911fe4eaf746f365e237c3e829c74509c55390413bfd6acab2b2be946f096c963d7f679aaffa99bcf72aa8fe28425c0a"))
            self.assertEqual(cmac_tdes2_tests[0]["KO"], bytearray.fromhex("e558419aa14e9b08f1cff74c18b8f00c967dcb1204e8ff43e0f0b0e742271c6341d077e460b7890a4434891bffbaf4b02dfcc9a357b5cc83ccf007276f180e70"))

            self.assertEqual(cmac_tdes2_tests[-1]["COUNT"], 39)
            self.assertEqual(cmac_tdes2_tests[-1]["L"], 2400)
            self.assertEqual(cmac_tdes2_tests[-1]["KI"], bytearray.fromhex("0e84ef2286a2b7fac0cd8d6251526740"))
            self.assertEqual(cmac_tdes2_tests[-1]["IVlen"], 64)
            self.assertEqual(cmac_tdes2_tests[-1]["IV"], bytearray.fromhex("4b75155f6170432b"))
            self.assertEqual(cmac_tdes2_tests[-1]["FixedInputDataByteLen"], 51)
            self.assertEqual(cmac_tdes2_tests[-1]["FixedInputData"], bytearray.fromhex("bdb999bd8839d983a268652f830c8ab1fdb767c776f3dfb75c2113e817a74e405aaa531116708901a34d55876962eb638aa069"))
            self.assertEqual(cmac_tdes2_tests[-1]["KO"], bytearray.fromhex("84bb964cb9c1b9395d9ab9b745c0adc5efd0dda24591f7bbcbf91b5acf61935aa2ae45adb1735b1f51c42fcdf3b7c32dafbbe7f076b980e30fea946955aaabfed1ea41608ab8c2a09602a4403db5bfdd8f58a5721241fb7a4b600e482a7d5a5886361a5c44ed90e776053895fec92c28c4922f3b7391cf43c271102671dd7576674934fb490793137e6cc9cd5943ef1b1c994c9723f54fe7685803dc2d27a07e2b0ffac5a024afc9ff6d4b7c7a54ef46063d6f4cce3bd48f9f047ad3092c5bfa8f89ca796487af434622fad2088f157b74590a3a240d3a4af274eca3020eb526ff6037e49af30e8bca5a344a73a03720e54f29eea3efc3c223f54bad514b188df9f384778efa087464bbee4d025b8d57a2502a3d29dad2c77234035f695ad5af75998886dcf7d2d8fe0d3cf1"))

            # First and last vector of the [PRF=HMAC_SHA1] profile
            self.assertEqual(hmac_sha1_tests[0]["COUNT"], 0)
            self.assertEqual(hmac_sha1_tests[0]["L"], 512)
            self.assertEqual(hmac_sha1_tests[0]["KI"], bytearray.fromhex("243c6e055084df1ac4bcc533f2d256c657fba0ee"))
            self.assertEqual(hmac_sha1_tests[0]["IVlen"], 160)
            self.assertEqual(hmac_sha1_tests[0]["IV"], bytearray.fromhex("06a645b26183a5fd3af5f46df48c4af6d7c1d424"))
            self.assertEqual(hmac_sha1_tests[0]["FixedInputDataByteLen"], 51)
            self.assertEqual(hmac_sha1_tests[0]["FixedInputData"], bytearray.fromhex("cfe7f9ca9960081cd8c4075b91bc40e980b96d262a8455145d961ab57e800616a27514cd8216603948487461dbbeabf1ff22f6"))
            self.assertEqual(hmac_sha1_tests[0]["KO"], bytearray.fromhex("9054ff3869dfb2be5a43a1108ab80d048a6ca69d398ef092346f6e382b32d311a48461df2e784bb7f359107d7062d6e3f55e373138dd03b4d39535ee1f046bd2"))

            self.assertEqual(hmac_sha1_tests[-1]["COUNT"], 39)
            self.assertEqual(hmac_sha1_tests[-1]["L"], 2400)
            self.assertEqual(hmac_sha1_tests[-1]["KI"], bytearray.fromhex("3159c07ab4a8233e57d629fd431046b75f4ace36"))
            self.assertEqual(hmac_sha1_tests[-1]["IVlen"], 160)
            self.assertEqual(hmac_sha1_tests[-1]["IV"], bytearray.fromhex("d466203d5041e61f09a15b6f5fbeff88fe4435c5"))
            self.assertEqual(hmac_sha1_tests[-1]["FixedInputDataByteLen"], 51)
            self.assertEqual(hmac_sha1_tests[-1]["FixedInputData"], bytearray.fromhex("9728436cbd75240e3c147834af03cc92cd7d8d7a35d0e31f0b1ecf43323da922a4568d88e1b88f5d2dc47d76e4f8922d571db7"))
            self.assertEqual(hmac_sha1_tests[-1]["KO"], bytearray.fromhex("5cf250aea5fd03b680191a1a5c4c42e199a88e880dca3383716d44fd72af01e29dd9f1ab485038c1c5a375e13c737c9fddf7f66acd4a57f212f89015d1c4e2c074d2df957acdab78a6722373c8f4c91c653a5834101dac7ec3b3e8d944e36ad5813f2887c9293f0565bc43fec552fa4b8372ac485bcc3615572ac24ae76a163b292901d475c841a2466bc54a296b7850b8ffb0b38b8b8424d73bd875bfa334168129876668eb5795d6b02205035ffd8ebf097f8ac63ffd877099b1af7cc2c3fa435e7539b42dca92f321bcefdd0d479135d8055ae7d3e416864cc203dd502093c3a3b019614102a610ca1ef306e0cbba5d98e2e8d905fa698ad6e3e2fb26e0068eb8f8a95bf08530c7b0dd31c2d8a3394d4da6c389b00406a80fe03104e1229df62c947755e411d8b371c3b9"))

            # First and last vector of the [PRF=HMAC_SHA512] profile
            self.assertEqual(hmac_sha512_tests[0]["COUNT"], 0)
            self.assertEqual(hmac_sha512_tests[0]["L"], 512)
            self.assertEqual(hmac_sha512_tests[0]["KI"], bytearray.fromhex("fbcf9b7b735b8676cc10691c7601563ec7f4b01914f6f46dfb32c1d4086c32dd6e02bc0883c655cc89a89f66e2fafcb7c591a792831d75c2440107f86549a2f0"))
            self.assertEqual(hmac_sha512_tests[0]["IVlen"], 512)
            self.assertEqual(hmac_sha512_tests[0]["IV"], bytearray.fromhex("6f68674090a820be3606272a36120e11de557ab794ad3e6f5d9b8c1b892cc29fc96a9ccaf3f5e3f1ca0fe8bd5df33e89a79b31dc04a6c73c2575dfd527c1b046"))
            self.assertEqual(hmac_sha512_tests[0]["FixedInputDataByteLen"], 51)
            self.assertEqual(hmac_sha512_tests[0]["FixedInputData"], bytearray.fromhex("44dacf2b3dc504f7ae55eee260646461f2a88c5f36dcd8393e3c3f79ce401315d7d66c7f0174576679db1aba3bf57cd742d0d1"))
            self.assertEqual(hmac_sha512_tests[0]["KO"], bytearray.fromhex("6d257eebfaa69b6e1d5fd7c360ea9e3d85a4f84c0d62713a0df1d0ff015956f2c3c8f8219e820f09360b0d267001787bdcc9264603338b032598d4afbe514bf3"))

            self.assertEqual(hmac_sha512_tests[-1]["COUNT"], 39)
            self.assertEqual(hmac_sha512_tests[-1]["L"], 2400)
            self.assertEqual(hmac_sha512_tests[-1]["KI"], bytearray.fromhex("5bad564345741ec8cac911b9527dc02b3a16d25d439f890983a97448bd71c63470baec0204dca3752765aa671569331c49e8f5708891410a8874661eef06adbe"))
            self.assertEqual(hmac_sha512_tests[-1]["IVlen"], 512)
            self.assertEqual(hmac_sha512_tests[-1]["IV"], bytearray.fromhex("36fc832a42a9cef443a226e102858eed00faef1aea3c1ed31f8607b76620a10e364840a0f4b0bf5e8772908397f7adf48583a948c24839dc9f09471005e25553"))
            self.assertEqual(hmac_sha512_tests[-1]["FixedInputDataByteLen"], 51)
            self.assertEqual(hmac_sha512_tests[-1]["FixedInputData"], bytearray.fromhex("499ced4f4ebabbbb80a7d86a19164fd6e1043cea1e00650b76c001273c6f2079d2f2df3e68b38880437ee6de6635018dfaeb0d"))
            self.assertEqual(hmac_sha512_tests[-1]["KO"], bytearray.fromhex("75aec3278b8574c96b99dffd7cf1698dcb0a570f7fc26060c6e94d2efa7368457c1d762a55374a25baf33054910038370e1acf1a51b7da3f90632af12d693ce91aca44aa9e63293f44280f997eea39ba80cd5215edfbc01f5a505dc75180b48079a2d8db6b0d53f9cdf83229a26e810aa93fa57b5eeaaea321a8e55266f02280ae3f713a848a855df1f9a813da98d78fd71876446246e37685ff6111158a592e3e2aeaea599aa21306ad301ca9a381b908134a6ec18e85408a757e98a7990599e371e61446d5a3d45119139503a41c34d6c372a9144d833364d9ec3ab4279da180249de2641e346019b99361e7fb26347d6d3d45b3f5830e34dad822b8eea256462ab45e341153fc98c354aa7067e3826ecb8c21cdfcec2a4fc85a5679c526c65029201442791a6118e58ba5"))
