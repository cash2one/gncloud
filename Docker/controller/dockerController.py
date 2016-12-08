# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import jsonify


# todo. Container 생성 및 실행
def doc_create():
    return jsonify(status=False, message="미구현")


# todo. Container 상태변경
def doc_state():
    return jsonify(status=False, message="미구현")


# todo. Container 삭제
def doc_delete():
    return jsonify(status=False, message="미구현")


# todo. Container 정보
def doc_vm():
    return jsonify(status=False, message="미구현")


# todo. Container 리스트
def doc_vm_list():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 생성 및 업로드
def doc_new_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 수정
def doc_modify_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 삭제
def doc_delete_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 리스트
def doc_image_list():
    return jsonify(status=False, message="미구현")
